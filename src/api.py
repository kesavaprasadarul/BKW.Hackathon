"""FastAPI Application Entry Point

Provides endpoints for:
1. Room type classification (upload Excel, run service.process)
2. Power requirements generation (merge heating & ventilation Excel files, run analysis)
3. Cost estimation (placeholder)

Environment: requires GOOGLE_GEMINI_API_KEY and GEMINI_API_KEY as per existing services.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import shutil
import time
import os
import pandas as pd

from roomtypes.service import process as classify_process
from roomtypes.models import Cfg
from power.merge_excel_files import merge_heating_ventilation_excel
from power.power_estimator import test_cost_analysis
from costestimator.main import generate_cost_estimate
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BKW Hackathon API", version="0.1.0")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.get("/health")
def health():
	return {"status": "ok"}


# -------------------------------
# Pydantic Models
# -------------------------------

class RoomTypeClassificationResponse(BaseModel):
	processed_file: str
	report_csv: str
	output_xlsx: str
	rows: int
	message: str

class PowerEstimates(BaseModel):
	room_nr: str
	room_type: int
	heating_W_per_m2: int
	cooling_W_per_m2: int
	ventilation_m3_per_h: int
	area_m2: float | None = None
	volume_m3: float | None = None

class PowerRequirementsResponse(BaseModel):
	heating_file: str
	ventilation_file: str
	merged_rows: int
	merged_columns: int
	power_estimates: Dict[str, PowerEstimates]
	performance_table: str
	message: str

class CostLineItem(BaseModel):
	subgroup_kg: str | None = None
	component_title: str | None = None
	quantity: float
	material_unit_price: float
	total_material_price: float
	total_final_price: float
	bki_component_title: str | None = None
	type: str | None = None

class CostEstimationSummary(BaseModel):
	project_metrics: Dict[str, float]
	grand_total_cost: float
	cost_factors_applied: Dict[str, float]

class CostEstimationResponse(BaseModel):
	summary: CostEstimationSummary
	detailed_boq: List[CostLineItem]
	message: str


# -------------------------------
# Helpers
# -------------------------------

UPLOAD_ROOT = Path("uploads")

def save_upload(file: UploadFile, subdir: str) -> Path:
	target_dir = UPLOAD_ROOT / subdir
	target_dir.mkdir(parents=True, exist_ok=True)
	ts = int(time.time() * 1000)
	filename = f"{ts}_{file.filename}"
	target_path = target_dir / filename
	with target_path.open("wb") as f:
		shutil.copyfileobj(file.file, f)
	return target_path

def _safe_float(val) -> Optional[float]:
	try:
		if val is None or (isinstance(val, str) and not val.strip()):
			return None
		return float(str(val).replace(',', '.'))
	except Exception:
		return None


# -------------------------------
# Endpoints (to be implemented next)
# -------------------------------

@app.post("/roomtypes/classify", response_model=RoomTypeClassificationResponse)
def classify_roomtypes(
	excel_file: UploadFile = File(..., description="Excel file containing room data"),
	mapping_csv: str = Form("../static/mapping/mapping.csv"),
):
	"""Classify room types from uploaded Excel and write Nummer Raumtyp into sheet.

	Returns paths to processed workbook and report CSV.
	"""
	try:
		saved = save_upload(excel_file, "roomtypes")
		mapping_path = Path(mapping_csv)
		if not mapping_path.exists():
			raise HTTPException(status_code=400, detail=f"Mapping CSV not found: {mapping_csv}")
		output_dir = Path("outputs/roomtypes")
		output_dir.mkdir(parents=True, exist_ok=True)
		output_xlsx = output_dir / f"classified_{saved.name}"
		report_csv = output_dir / f"report_{saved.stem}.csv"
		cfg = Cfg()
		classify_process(
			mapping_csv=mapping_path,
			target_xlsx=saved,
			output_xlsx=output_xlsx,
			report_csv=report_csv,
			cfg=cfg,
		)
		# Get row count using pandas (first sheet)
		import openpyxl
		wb = openpyxl.load_workbook(output_xlsx, read_only=True)
		ws = wb.worksheets[0]
		rows = ws.max_row
		return RoomTypeClassificationResponse(
			processed_file=str(saved),
			report_csv=str(report_csv),
			output_xlsx=str(output_xlsx),
			rows=rows,
			message="Classification complete",
		)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/power/requirements", response_model=PowerRequirementsResponse)
async def generate_power_requirements(
	heating_file: UploadFile = File(...),
	ventilation_file: UploadFile = File(...),
):
	"""Generate power requirements by merging heating & ventilation Excel files and running analysis."""
	try:
		saved_heating = save_upload(heating_file, "power")
		saved_ventilation = save_upload(ventilation_file, "power")

		# Merge files with AI structure detection
		merged_df = await merge_heating_ventilation_excel(
			str(saved_heating),
			str(saved_ventilation),
			auto_detect_structure=True,
		)

		# Hard-coded types mapping (could be externalized later)
		types = {
			1: "Flex-/ Co-Work/",
			2: "Einzel-/Zweierbüros",
			3: "Technikum",
			4: "Smart Farming",
			5: "Robotik",
			6: "Verkehrsflächen, Flure",
			7: "Teeküchen",
			8: "WCs",
			9: "ELT-Zentrale",
			10: "Putzmittel/ Lager",
			11: "Lager innenliegend",
			12: "TGA-Zentrale",
			13: "Etagenverteiler",
			14: "ELT-Schacht",
			15: "Batterieräume",
			16: "Drucker-/Kopierräume",
			17: "Treppenhäuser/Magistrale",
			18: "Schächte",
			19: "Aufzüge",
			20: "Serminarraum",
			21: "Diele",
		}

		estimates = await test_cost_analysis(merged_df, skip_structure_analysis=True, types=types)

		performance_table_path = Path("performance_table.xlsx")
		# Ensure required key column exists
		if 'Raum-Nr.' not in merged_df.columns:
			raise HTTPException(status_code=400, detail="Merged dataframe missing 'Raum-Nr.' column")

		def _nan_to_none(val):
			"""Convert pandas NaN/inf or invalid numeric to None for JSON compliance."""
			try:
				if val is None:
					return None
				# pandas uses numpy NaN, check via pandas.isna
				import math
				if isinstance(val, (float, int)):
					if math.isnan(val) or math.isinf(val):
						return None
				if hasattr(val, 'dtype') and str(val.dtype).startswith('float'):
					# handle numpy scalar
					if pd.isna(val):
						return None
				record = float(val) if isinstance(val, (pd.Series,)) else val
				return val
			except Exception:
				return None

		response_estimates: Dict[str, PowerEstimates] = {}
		for k, v in estimates.items():
			room_df = merged_df.loc[merged_df['Raum-Nr.'] == k]
			area_val = None
			vol_val = None
			if 'Fläche_heating' in merged_df.columns and not room_df.empty:
				try:
					area_val = room_df['Fläche_heating'].iloc[0]
				except Exception:
					area_val = None
			if 'Volumen_heating' in merged_df.columns and not room_df.empty:
				try:
					vol_val = room_df['Volumen_heating'].iloc[0]
				except Exception:
					vol_val = None
			response_estimates[k] = PowerEstimates(
				room_nr=k,
				room_type=int(v.get("room_type", 0) or 0),
				heating_W_per_m2=int(_nan_to_none(v.get("heating_W_per_m2")) or 0),
				cooling_W_per_m2=int(_nan_to_none(v.get("cooling_W_per_m2")) or 0),
				ventilation_m3_per_h=int(_nan_to_none(v.get("ventilation_m3_per_h")) or 0),
				area_m2=_nan_to_none(area_val),
				volume_m3=_nan_to_none(vol_val),
			)
		return PowerRequirementsResponse(
			heating_file=str(saved_heating),
			ventilation_file=str(saved_ventilation),
			merged_rows=merged_df.shape[0],
			merged_columns=merged_df.shape[1],
			power_estimates=response_estimates,
			performance_table=str(performance_table_path) if performance_table_path.exists() else "",
			message="Power requirements generated",
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/cost/estimate", response_model=CostEstimationResponse)
def cost_estimate(request: PowerRequirementsResponse):
	"""Generate a cost estimate using the previously produced power requirements payload."""
	try:
		if not request.power_estimates:
			raise HTTPException(status_code=400, detail="power_estimates cannot be empty")
		# Delegate to cost estimation engine
		result = generate_cost_estimate(request)
		line_items = []
		for li in result.get('detailed_boq', []):
			line_items.append(CostLineItem(
				subgroup_kg=li.get('subgroup_kg'),
				component_title=li.get('title') or li.get('component_title'),
				quantity=li.get('quantity', 0),
				material_unit_price=li.get('material_unit_price', 0),
				total_material_price=li.get('total_material_price', 0),
				total_final_price=li.get('total_final_price', 0),
				bki_component_title=li.get('bki_component_title'),
				type=li.get('type'),
			))
		summary_raw = result.get('summary', {})
		summary = CostEstimationSummary(
			project_metrics=summary_raw.get('project_metrics', {}),
			grand_total_cost=summary_raw.get('grand_total_cost', 0),
			cost_factors_applied=summary_raw.get('cost_factors_applied', {}),
		)
		return CostEstimationResponse(summary=summary, detailed_boq=line_items, message="Cost estimation complete")
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


# Routers will be added below in subsequent steps.

if __name__ == "__main__":
	# Development server startup (optional): uvicorn main:app --reload
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
