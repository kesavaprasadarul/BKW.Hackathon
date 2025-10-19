# Atrium AI - UI Design Specification

## Project Overview

Atrium AI is an intelligent platform that transforms decades of engineering and construction knowledge into predictive insights. It forecasts heating demand, energy costs, and material performance to help companies design and operate buildings more efficiently.

---

## Design Philosophy

### Core Principles
- **Minimalist & Modern**: Clean, uncluttered interfaces with purposeful white space
- **Elegant Legacy**: Professional aesthetic with sophisticated blue tones
- **Data-Driven Clarity**: Information hierarchy that guides users through complex data
- **No Box-on-Box**: Avoid excessive container nesting and gray-shaded boxes
- **Breathable Design**: Let content float naturally on clean backgrounds

---

## Color Palette

### Primary Colors
```css
--primary-blue: #5B8DBE        /* Elegant legacy blue - main brand */
--primary-blue-dark: #3D5A80   /* Darker shade for contrast */
--primary-blue-light: #A8C5E3  /* Light pastel for backgrounds */
--accent-blue: #7BA3CC         /* Interactive elements */
```

### Neutral Colors
```css
--background: #FAFBFC          /* Off-white, warm background */
--surface: #FFFFFF             /* Pure white for cards */
--text-primary: #1F2937        /* Almost black for primary text */
--text-secondary: #6B7280      /* Gray for secondary text */
--border-light: #E5E7EB        /* Subtle borders */
```

### Semantic Colors
```css
--success-green: #86BCAC       /* Pastel green for optimized results */
--warning-amber: #F0C987       /* Pastel amber for standard scenario */
--error-red: #E8A09F           /* Pastel red for warnings */
```

---

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Type Scale
- **Display**: text-4xl to text-6xl, font-bold (Headings, Hero text)
- **Heading**: text-2xl to text-3xl, font-semibold (Section titles)
- **Subheading**: text-xl, font-medium (Card titles)
- **Body**: text-base, font-normal (Regular content)
- **Small**: text-sm, font-normal (Captions, labels)
- **Tiny**: text-xs, font-medium (Tags, metadata)

---

## Iconography

### Primary Icon Set
Use **Lucide React** icons exclusively for consistency.

### Brand Logo
- Icon: `<DraftingCompass />` from lucide-react
- Size: 32px standard, 40px large contexts
- Color: Primary blue (#5B8DBE)

### Functional Icons
- **Upload**: `<Upload />`, `<FileUp />`
- **Progress**: `<Loader2 />`, `<CheckCircle2 />`
- **Analysis**: `<Brain />`, `<TrendingUp />`
- **Export**: `<Download />`, `<FileDown />`
- **Comparison**: `<GitCompare />`, `<BarChart3 />`
- **Energy**: `<Zap />`, `<Flame />`
- **Report**: `<FileText />`, `<ClipboardList />`

---

## Layout System

### Grid Structure
```
Container max-width: 1280px (xl)
Padding: px-6 md:px-8 lg:px-12
Gap between sections: 64px (space-y-16)
Gap between components: 32px (space-y-8)
```

### Responsive Breakpoints
```
sm: 640px   (mobile landscape)
md: 768px   (tablet portrait)
lg: 1024px  (tablet landscape)
xl: 1280px  (desktop)
2xl: 1536px (large desktop)
```

---

## Component Library

### 1. Navigation Header
**Design:**
- Fixed top position with subtle backdrop blur
- Height: 72px
- Transparent background with border-bottom (border-light)
- Logo (DraftingCompass) + "Atrium AI" wordmark on left
- Navigation items centered (if needed)
- User profile/settings on right

**Tailwind Classes:**
```
fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50
```

---

### 2. Hero Section (Home Page)
**Design:**
- Full viewport height minus header
- Centered content with max-width-2xl
- Clean background gradient (subtle blue tint)
- Large icon (DraftingCompass) at 64px
- Headline + subtitle + upload area
- No heavy boxes, just content on clean background

**Structure:**
```
[DraftingCompass Icon - 64px]
[Headline: "Transform Engineering Data into Predictive Insights"]
[Subtitle: "Upload your Leistungsermittlung to get started"]
[Upload Area - Drag & Drop Zone]
```

**Upload Area Styling:**
- Large dashed border (border-dashed border-primary-blue)
- Rounded corners (rounded-2xl)
- Padding: py-16 px-8
- Hover state: subtle blue background
- Icon: Upload (48px)

---

### 3. Progress Stepper Bar
**Design:**
- Fixed position below header OR sticky at top of content
- Horizontal step indicator showing 3 stages
- Clean line connecting steps
- Active step highlighted in primary blue
- Completed steps with checkmark icon

**Steps:**
1. **Raumtyp Optimierung** (Room Type Optimization)
   - Icon: `<Home />` or `<Building />`
   
2. **Energieverbrauch Prognose** (Energy Consumption Forecast)
   - Icon: `<Zap />` or `<Gauge />`
   - Shows W/m² prediction
   
3. **Finaler Bericht** (Final Report)
   - Icon: `<FileText />` or `<ClipboardCheck />`

**Visual Structure:**
```
[1] ————— [2] ————— [3]
Active: filled circle with icon (primary-blue)
Completed: checkmark in circle (success-green)
Pending: outlined circle (border-light)
```

**Tailwind Implementation:**
```
Container: flex items-center justify-between max-w-2xl mx-auto
Step: flex flex-col items-center gap-2
Connector: flex-1 border-t-2 mx-4
```

---

### 4. Processing/Loading State
**Design:**
- Centered content area
- Animated spinner (Loader2 with spin animation)
- Processing step name below
- Estimated time or progress percentage
- Clean, minimal - no heavy boxes

**Animation:**
```
animate-spin (for Loader2 icon)
Pulse effect on text: animate-pulse
```

---

### 5. Results Cards (Step Outputs)
**Design:**
- Clean white cards with subtle shadow (not gray boxes)
- Rounded corners (rounded-xl)
- Padding: p-6 to p-8
- Light border (border border-gray-100)
- Hover: slight shadow increase (transition-shadow)

**Card Structure:**
```
[Icon] [Title]
[Value/Metric - Large typography]
[Supporting text or delta]
```

**Example - Step 2 Output:**
```
[Zap Icon] Optimierter Energieverbrauch
45 W/m²
↓ 18% gegenüber Standard
```

---

### 6. Final Report Section
**Design:**
- Two-column layout on desktop (single column mobile)
- Left: Report summary with key metrics
- Right: Export options and actions

**Key Metrics Display:**
- Large numbers with units
- Color-coded based on optimization (success-green for improvements)
- Icons for each metric category
- Clean spacing between metrics (space-y-6)

**Export Button:**
- Primary blue background
- Icon: Download
- Text: "Bericht Exportieren"
- Hover state with darker blue
- Classes: `bg-primary-blue hover:bg-primary-blue-dark text-white px-6 py-3 rounded-lg`

---

### 7. Comparison Section (Critical Component)
**Design:**
- Full-width section with clean background
- Title: "Effizienzvergleich" or "Scenario Comparison"
- Side-by-side comparison layout

**Two-Scenario Cards:**

**Standard Scenario (Left):**
- Header background: warning-amber (pastel amber)
- Icon: Building or Home
- Title: "Standard-Szenario"
- Metrics list with values

**AI-Optimized Scenario (Right):**
- Header background: success-green (pastel green)
- Icon: Brain or Sparkles
- Title: "KI-Optimiertes Szenario"
- Metrics list with values
- Delta indicators showing improvement

**Visual Differences:**
- Use color-coded backgrounds for headers only
- Main card body stays white
- Highlight changed parameters with subtle background tint
- Delta arrows (↓ for reductions, ↑ for increases)

---

### 8. Cost Projection Chart
**Design:**
- Bar chart or line chart showing yearly projections
- Two data series:
  - Standard scenario (amber/warm color)
  - AI-optimized scenario (green/cool color)
- X-axis: Months or quarters
- Y-axis: Cost in Euros (€)
- Legend clearly showing both scenarios
- Clean grid lines (very subtle)

**Recharts Implementation:**
```jsx
<LineChart>
  <Line 
    dataKey="standard" 
    stroke="#F0C987" 
    name="Standard" 
  />
  <Line 
    dataKey="optimized" 
    stroke="#86BCAC" 
    name="AI-Optimiert" 
  />
</LineChart>
```

**Below Chart:**
- Savings calculation box
- Large number showing total savings
- Percentage improvement
- Icon: TrendingDown or PiggyBank

---

### 9. Parameter Difference Display
**Design:**
- Table or card grid showing key parameters
- Columns: Parameter Name | Standard | Optimized | Delta
- Color-coded deltas (green for improvements)
- Icons for each parameter type

**Example Parameters:**
- Raumtyp (Room Type)
- Heizleistung W/m² (Heating Power)
- Jahresverbrauch kWh (Annual Consumption)
- Kosten/Jahr € (Cost per Year)

**Styling:**
```
Clean table with:
- Header row (text-sm font-medium text-secondary)
- Body rows with hover effect
- Aligned columns (left for names, right for numbers)
- No heavy borders, just subtle separators
```

---

## Page Layouts

### Home Page Layout
```
[Navigation Header - Fixed]
[Hero Section - Full viewport]
  - Logo/Icon centered
  - Headline
  - Subtitle
  - Upload Area (prominent)
  - "How it works" brief description below

[Footer - Minimal]
```

### Processing/Analysis Page
```
[Navigation Header]

[Progress Stepper - Sticky]

[Current Step Display]
  - Step icon and name
  - Loading animation
  - Status message

[Background: Clean gradient or pattern]
```

### Results Page (Step 1 & 2)
```
[Navigation Header]

[Progress Stepper]

[Results Section]
  - Step title
  - Key metric cards (2-3 cards in row)
  - Supporting information
  - "Continue" button to next step

[Background: Clean white]
```

### Final Report Page (Step 3)
```
[Navigation Header]

[Progress Stepper - All completed]

[Report Header Section]
  - Title: "Analyse Abgeschlossen"
  - Project metadata
  - Export button (prominent, top-right)

[Key Metrics Grid]
  - 4-6 metric cards showing final values

[Comparison Section - Full Width]
  - "Effizienzvergleich" heading
  - Two-scenario cards side by side
  - Parameter difference table

[Cost Projection Section]
  - "Kosteneinsparungen" heading
  - Chart showing yearly projections
  - Savings summary card

[Detailed Breakdown - Accordion or Tabs]
  - Additional technical details
  - Recommendations
  - Methodology notes

[Footer with metadata]
```

---

## Responsive Behavior

### Mobile (< 768px)
- Stack all cards vertically
- Full-width components
- Stepper becomes vertical or scrollable horizontal
- Charts responsive with proper sizing
- Upload area reduces padding
- Hide secondary information, show on expand

### Tablet (768px - 1024px)
- Two-column layouts where appropriate
- Charts at optimal size
- Comfortable spacing
- Readable typography

### Desktop (> 1024px)
- Multi-column layouts
- Side-by-side comparisons
- Full stepper horizontal
- Maximum chart width for readability
- Optimal line lengths for text

---

## Animations & Transitions

### Subtle Micro-interactions
```css
/* Default transitions */
transition-all duration-200 ease-in-out

/* Hover effects */
hover:shadow-lg hover:scale-[1.02]

/* Loading states */
animate-pulse (for text/placeholders)
animate-spin (for spinners)

/* Entrance animations */
fade-in: opacity-0 to opacity-100
slide-up: translate-y-4 to translate-y-0
```

### Page Transitions
- Smooth fade between steps
- Progressive disclosure of results
- Staggered animation for card grids

---

## Technical Implementation Notes

### File Upload Component
```jsx
- Accept: .xlsx, .xls
- Max size: 10MB
- Drag and drop functionality
- File name display after upload
- Remove/replace option
- Validation feedback
```

### Backend Integration Points
```
POST /api/upload - Upload Leistungsermittlung
GET /api/analysis/{id}/step1 - Get room type optimization
GET /api/analysis/{id}/step2 - Get energy prediction
GET /api/analysis/{id}/step3 - Get final report
GET /api/export/{id} - Export report PDF
```

### State Management
- Loading states for each step
- Error handling with user-friendly messages
- Progress persistence (save state if user refreshes)
- Cache responses as mentioned (hardcoded for now)

---

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus states clearly visible
- Color contrast ratios meeting WCAG AA
- Alt text for all icons and images
- Screen reader friendly labels

---

## Sample Component Code Snippets

### Upload Area Component
```jsx
<div className="max-w-2xl mx-auto p-8">
  <div className="border-2 border-dashed border-primary-blue rounded-2xl p-16 text-center hover:bg-blue-50/30 transition-colors cursor-pointer">
    <Upload className="w-12 h-12 mx-auto text-primary-blue mb-4" />
    <p className="text-lg font-medium text-gray-900 mb-2">
      Leistungsermittlung hochladen
    </p>
    <p className="text-sm text-gray-600">
      Ziehen Sie Ihre Excel-Datei hierher oder klicken Sie zum Auswählen
    </p>
  </div>
</div>
```

### Metric Card Component
```jsx
<div className="bg-white rounded-xl p-6 border border-gray-100 hover:shadow-lg transition-shadow">
  <div className="flex items-start gap-3">
    <div className="p-2 bg-blue-100 rounded-lg">
      <Zap className="w-5 h-5 text-primary-blue" />
    </div>
    <div className="flex-1">
      <p className="text-sm font-medium text-gray-600 mb-1">
        Energieverbrauch
      </p>
      <p className="text-3xl font-bold text-gray-900">
        45 W/m²
      </p>
      <p className="text-sm text-success-green mt-2">
        ↓ 18% optimiert
      </p>
    </div>
  </div>
</div>
```

### Progress Stepper Component
```jsx
<div className="max-w-2xl mx-auto py-8">
  <div className="flex items-center justify-between">
    {steps.map((step, index) => (
      <div key={index} className="flex flex-col items-center flex-1">
        <div className={`
          w-12 h-12 rounded-full flex items-center justify-center
          ${step.completed ? 'bg-success-green' : 
            step.active ? 'bg-primary-blue' : 'border-2 border-gray-300'}
        `}>
          {step.completed ? (
            <CheckCircle2 className="w-6 h-6 text-white" />
          ) : (
            <step.icon className="w-6 h-6 text-white" />
          )}
        </div>
        <p className="text-sm font-medium mt-2 text-center">
          {step.name}
        </p>
      </div>
      {index < steps.length - 1 && (
        <div className="flex-1 border-t-2 border-gray-300 mx-4 mt-6" />
      )}
    ))}
  </div>
</div>
```

### Comparison Cards Component
```jsx
<div className="grid md:grid-cols-2 gap-6">
  {/* Standard Scenario */}
  <div className="bg-white rounded-xl overflow-hidden border border-gray-100">
    <div className="bg-warning-amber/30 px-6 py-4 border-b border-warning-amber/50">
      <div className="flex items-center gap-2">
        <Building className="w-5 h-5" />
        <h3 className="font-semibold">Standard-Szenario</h3>
      </div>
    </div>
    <div className="p-6 space-y-4">
      {/* Metrics */}
    </div>
  </div>
  
  {/* AI-Optimized Scenario */}
  <div className="bg-white rounded-xl overflow-hidden border border-gray-100">
    <div className="bg-success-green/30 px-6 py-4 border-b border-success-green/50">
      <div className="flex items-center gap-2">
        <Brain className="w-5 h-5" />
        <h3 className="font-semibold">KI-Optimiertes Szenario</h3>
      </div>
    </div>
    <div className="p-6 space-y-4">
      {/* Metrics with deltas */}
    </div>
  </div>
</div>
```

---

## Design System Summary

**DO:**
- Use generous white space
- Let content breathe on clean backgrounds
- Employ subtle shadows and borders
- Use pastel blues and elegant legacy tones
- Implement smooth, purposeful animations
- Maintain consistent icon sizing and style
- Follow clear information hierarchy

**DON'T:**
- Create boxes within boxes with gray shades
- Overuse borders and dividers
- Use harsh, saturated colors
- Implement heavy drop shadows
- Clutter the interface with unnecessary elements
- Mix icon styles from different libraries

---

## Development Workflow

1. **Setup Phase**
   - Initialize React project with TypeScript
   - Install Tailwind CSS and configure theme
   - Install lucide-react for icons
   - Install recharts for data visualization
   - Set up routing (React Router)

2. **Component Development**
   - Build component library first
   - Create storybook/component showcase
   - Implement responsive breakpoints
   - Test on multiple devices

3. **Page Assembly**
   - Assemble pages from components
   - Implement routing and navigation
   - Add state management
   - Connect to backend APIs (mock first)

4. **Polish & Refinement**
   - Fine-tune animations
   - Optimize performance
   - Accessibility audit
   - Cross-browser testing

---

## Future Enhancements

- Dark mode support
- Multi-language support (German/English toggle)
- Export to multiple formats (PDF, Excel, JSON)
- Historical analysis comparison
- Project saved states and history
- Collaborative features
- Advanced filtering and sorting

---

## Notes

This specification provides the foundation for building Atrium AI's user interface. The design emphasizes clarity, elegance, and data-driven decision-making while maintaining a clean, modern aesthetic. All components should be built with responsiveness and accessibility in mind from the start.

For mockups and prototypes, refer to this specification and use the whiteboard image as reference for workflow logic.