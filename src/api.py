"""FastAPI Application Entry Point

Provides endpoints for:
1. Room type classification (upload Excel, run service.process)
2. Power requirements generation (merge heating & ventilation Excel files, run analysis)
3. Cost estimation (placeholder)

Environment: requires GOOGLE_GEMINI_API_KEY and GEMINI_API_KEY as per existing services.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
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
from reporting.extractor import FileExtractor
from reporting.designer import Designer
from ai import AIService
from reporting.agent import DataAgent
import uuid

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


@app.get("/download")
def download_file(file: str):
    """Download a file from the server."""
    try:
        file_path = Path(file)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Security check: ensure file is within allowed directories
        allowed_dirs = [Path("outputs"), Path("uploads"), Path("static")]
        if not any(
            str(file_path).startswith(str(allowed_dir)) for allowed_dir in allowed_dirs
        ):
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


class CostBOQItem(BaseModel):
    description: str
    subgroup_kg: Optional[str] = None
    subgroup_title: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    material_unit_price: float
    total_material_price: float
    total_final_price: float
    bki_component_title: str
    type: Optional[str] = None


class CostEstimationSummary(BaseModel):
    project_metrics: Dict[str, float]
    grand_total_cost: float
    cost_factors_applied: Dict[str, float]


class CostEstimationOutput(BaseModel):
    summary: CostEstimationSummary
    detailed_boq: List[CostBOQItem]


class ReportGenerateResponse(BaseModel):
    project_name: str
    file_count: int
    formats_generated: List[str]
    pdf_path: Optional[str] = None
    docx_path: Optional[str] = None
    markdown_path: Optional[str] = None
    message: str


class AgentCreateResponse(BaseModel):
    agent_id: str
    file_count: int
    message: str


class AgentAskRequest(BaseModel):
    agent_id: str
    question: str


class AgentAskResponse(BaseModel):
    agent_id: str
    question: str
    answer: str
    cached: bool


# -------------------------------
# Helpers
# -------------------------------

UPLOAD_ROOT = Path("uploads")
_AGENTS: Dict[str, DataAgent] = {}


def save_upload(file: UploadFile, subdir: str) -> Path:
    target_dir = UPLOAD_ROOT / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time() * 1000)
    filename = f"{ts}_{file.filename}"
    target_path = target_dir / filename
    with target_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return target_path


def _new_agent_id() -> str:
    return uuid.uuid4().hex


def _safe_float(val) -> Optional[float]:
    try:
        if val is None or (isinstance(val, str) and not val.strip()):
            return None
        return float(str(val).replace(",", "."))
    except Exception:
        return None


# -------------------------------
# Endpoints (to be implemented next)
# -------------------------------


@app.post("/roomtypes/classify", response_model=RoomTypeClassificationResponse)
def classify_roomtypes(
    excel_file: UploadFile = File(..., description="Excel file containing room data"),
    mapping_csv: UploadFile = File(..., description="Mapping CSV file"),
):
    """Classify room types from uploaded Excel and write Nummer Raumtyp into sheet.

    Returns paths to processed workbook and report CSV.
    """
    try:
        saved = save_upload(excel_file, "roomtypes")
        mapping_path = save_upload(mapping_csv, "roomtypes")
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

        estimates = await test_cost_analysis(
            merged_df, skip_structure_analysis=True, types=types
        )

        performance_table_path = Path("performance_table.xlsx")
        # Ensure required key column exists
        if "Raum-Nr." not in merged_df.columns:
            raise HTTPException(
                status_code=400, detail="Merged dataframe missing 'Raum-Nr.' column"
            )

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
                if hasattr(val, "dtype") and str(val.dtype).startswith("float"):
                    # handle numpy scalar
                    if pd.isna(val):
                        return None
                record = float(val) if isinstance(val, (pd.Series,)) else val
                return val
            except Exception:
                return None

        response_estimates: Dict[str, PowerEstimates] = {}
        for k, v in estimates.items():
            room_df = merged_df.loc[merged_df["Raum-Nr."] == k]
            area_val = None
            vol_val = None
            if "Fläche_heating" in merged_df.columns and not room_df.empty:
                try:
                    area_val = room_df["Fläche_heating"].iloc[0]
                except Exception:
                    area_val = None
            if "Volumen_heating" in merged_df.columns and not room_df.empty:
                try:
                    vol_val = room_df["Volumen_heating"].iloc[0]
                except Exception:
                    vol_val = None
            response_estimates[k] = PowerEstimates(
                room_nr=k,
                room_type=int(v.get("room_type", 0) or 0),
                heating_W_per_m2=int(_nan_to_none(v.get("heating_W_per_m2")) or 0),
                cooling_W_per_m2=int(_nan_to_none(v.get("cooling_W_per_m2")) or 0),
                ventilation_m3_per_h=int(
                    _nan_to_none(v.get("ventilation_m3_per_h")) or 0
                ),
                area_m2=_nan_to_none(area_val),
                volume_m3=_nan_to_none(vol_val),
            )
        return PowerRequirementsResponse(
            heating_file=str(saved_heating),
            ventilation_file=str(saved_ventilation),
            merged_rows=merged_df.shape[0],
            merged_columns=merged_df.shape[1],
            power_estimates=response_estimates,
            performance_table=(
                str(performance_table_path) if performance_table_path.exists() else ""
            ),
            message="Power requirements generated",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cost/estimate", response_model=CostEstimationOutput)
def cost_estimate(request: PowerRequirementsResponse):
    """Generate a cost estimate using the previously produced power requirements payload.

    Response format matches final_estimate_output.json (summary + detailed_boq)."""
    try:
        if not request.power_estimates:
            raise HTTPException(
                status_code=400, detail="power_estimates cannot be empty"
            )
        result = generate_cost_estimate(request)
        summary_raw = result.get("summary", {})
        summary = CostEstimationSummary(
            project_metrics=summary_raw.get("project_metrics", {}),
            grand_total_cost=summary_raw.get("grand_total_cost", 0),
            cost_factors_applied=summary_raw.get("cost_factors_applied", {}),
        )
        allowed_fields = {
            "description",
            "subgroup_kg",
            "subgroup_title",
            "quantity",
            "unit",
            "material_unit_price",
            "total_material_price",
            "total_final_price",
            "bki_component_title",
            "type",
        }
        boq_items: List[CostBOQItem] = []
        for li in result.get("detailed_boq", []):
            filtered = {k: v for k, v in li.items() if k in allowed_fields}
            # Some templates may use 'title' instead of 'description'
            if "description" not in filtered and "title" in li:
                filtered["description"] = li.get("title")
            # Ensure mandatory keys exist
            filtered.setdefault("description", "N/A")
            filtered.setdefault("bki_component_title", "N/A")
            filtered.setdefault("quantity", 0)
            filtered.setdefault("material_unit_price", 0)
            filtered.setdefault("total_material_price", 0)
            filtered.setdefault("total_final_price", 0)
            boq_items.append(CostBOQItem(**filtered))
        return CostEstimationOutput(summary=summary, detailed_boq=boq_items)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/report/generate", response_model=ReportGenerateResponse)
async def generate_report(
    files: List[UploadFile] = File(..., description="Multiple project context files"),
    project_name: str = Form("Projekt"),
    formats: str = Form("pdf"),  # comma separated: pdf,docx,md,all
    download: bool = Form(False),  # if true return file directly (single or zip)
) -> ReportGenerateResponse | FileResponse:
    """Generate Erläuterungsbericht from uploaded context files.

    Steps:
    1. Save uploads to a temp dir under uploads/reporting
    2. Extract text using FileExtractor
    3. Run AIService.generate_report_chunked
    4. Produce requested formats via Designer
    """
    try:
        print("[report] starting generation", project_name, "files=", len(files))
        if not files:
            print("[report] no files provided")
            raise HTTPException(status_code=400, detail="No files uploaded")
        target_dir = UPLOAD_ROOT / "reporting" / f"session_{int(time.time())}"
        target_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        for f in files:
            path = target_dir / f.filename
            with path.open("wb") as out:
                shutil.copyfileobj(f.file, out)
            saved_paths.append(path)

        extractor = FileExtractor()
        extracted_map = {}
        print("[report] saved", len(saved_paths), "files to", target_dir)
        for p in saved_paths:
            content = extractor.extract_from_file(p)
            if content:
                extracted_map[p.name] = content
        if not extracted_map:
            raise HTTPException(
                status_code=400, detail="Could not extract content from any file"
            )
        combined_text = extractor.combine_extracted_data(
            extracted_map, project_name=project_name
        )
        print("[report] combined text length", len(combined_text))

        # AI generation
        try:
            ai = AIService()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"AI initialization failed: {e}"
            )
        report_content = ai.generate_report_chunked(combined_text)
        print(
            "[report] generated content length",
            len(report_content) if report_content else 0,
        )
        if not report_content:
            raise HTTPException(
                status_code=500, detail="Report generation produced no content"
            )

        designer = Designer()
        requested = [s.strip().lower() for s in formats.split(",") if s.strip()]
        if "all" in requested:
            requested = ["pdf", "docx", "md"]
        generated = []
        pdf_path = docx_path = markdown_path = None
        if "pdf" in requested:
            pdf_path = designer.pdf(report_content, doc_title="Erläuterungsbericht")
            generated.append("pdf")
        if "docx" in requested:
            docx_path = designer.docx(report_content, doc_title="Erläuterungsbericht")
            generated.append("docx")
        if "md" in requested or "markdown" in requested:
            markdown_path = designer.markdown(report_content)
            generated.append("md")

        # If download requested, return the file directly (zip if multiple)
        if download and generated:
            # Choose behavior: if more than 1 format, zip them
            files_to_send = []
            if pdf_path:
                files_to_send.append(pdf_path)
            if docx_path:
                files_to_send.append(docx_path)
            if markdown_path:
                files_to_send.append(markdown_path)
            if len(files_to_send) == 1:
                return FileResponse(
                    files_to_send[0],
                    filename=Path(files_to_send[0]).name,
                    media_type="application/octet-stream",
                )
            else:
                zip_name = f"report_bundle_{int(time.time())}.zip"
                zip_path = UPLOAD_ROOT / "reporting" / zip_name
                import zipfile

                with zipfile.ZipFile(
                    zip_path, "w", compression=zipfile.ZIP_DEFLATED
                ) as zf:
                    for fp in files_to_send:
                        zf.write(fp, arcname=Path(fp).name)
                return FileResponse(
                    str(zip_path), filename=zip_name, media_type="application/zip"
                )
        resp = ReportGenerateResponse(
            project_name=project_name,
            file_count=len(saved_paths),
            formats_generated=generated,
            pdf_path=pdf_path,
            docx_path=docx_path,
            markdown_path=markdown_path,
            message="Report generated successfully",
        )
        print("[report] returning JSON response", resp.formats_generated)
        return resp
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/create", response_model=AgentCreateResponse)
async def agent_create(
    files: List[UploadFile] = File(
        ..., description="Context files for interactive agent"
    ),
    project_name: str = Form("Projekt"),
):
    """Create a DataAgent with uploaded context files and return agent_id."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        session_dir = UPLOAD_ROOT / "agent" / f"session_{int(time.time())}"
        session_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        for f in files:
            p = session_dir / f.filename
            with p.open("wb") as out:
                shutil.copyfileobj(f.file, out)
            saved_paths.append(p)
        agent = DataAgent()
        agent.load_data(session_dir)
        agent_id = _new_agent_id()
        _AGENTS[agent_id] = agent
        return AgentCreateResponse(
            agent_id=agent_id, file_count=len(saved_paths), message="Agent created"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/ask", response_model=AgentAskResponse)
async def agent_ask(payload: AgentAskRequest):
    """Ask a question to an existing DataAgent."""
    agent = _AGENTS.get(payload.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="agent_id not found")
    answer = agent.ask(payload.question)
    cached = bool(agent.cache)
    return AgentAskResponse(
        agent_id=payload.agent_id,
        question=payload.question,
        answer=answer,
        cached=cached,
    )


@app.delete("/agent/delete/{agent_id}")
def agent_delete(agent_id: str):
    """Delete an existing DataAgent and clean up cache."""
    agent = _AGENTS.pop(agent_id, None)
    if not agent:
        raise HTTPException(status_code=404, detail="agent_id not found")
    try:
        agent.cleanup()
    except Exception:
        pass
    return {"agent_id": agent_id, "message": "Agent deleted"}


# Routers will be added below in subsequent steps.

if __name__ == "__main__":
    # Development server startup (optional): uvicorn main:app --reload
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
