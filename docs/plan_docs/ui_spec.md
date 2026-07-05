# D1.5: UI Specification & Dynamic Rendering

This document describes the **UI Schema Generator**, outlines the dynamic form rendering architecture for SwiftUI and JavaScript web platforms, and provides wireframe designs.

---

## D1.5: UI Schema Generator

The **UI Schema** translates technical execution profile properties and limits into localized visual rendering instructions. Instead of hardcoding fields in Swift or HTML, the UI fetches a schema that dictates what sections to draw, what input types to use, and how to validate inputs.

### UI Schema Response (JSON Structure)

```json
{
  "profile_name": "nemotron_triage",
  "groups": [
    {
      "id": "autoregressive",
      "label": "Autoregressive Parameters",
      "description": "Basic causal token parameters",
      "controls": [
        {
          "key": "temperature",
          "control_type": "slider",
          "label": "Temperature",
          "tooltip": "Sampling temperature. Higher is more creative.",
          "value_type": "float",
          "default": 0.7,
          "min": 0.0,
          "max": 2.0,
          "step": 0.05,
          "visibility": "standard"
        },
        {
          "key": "top_p",
          "control_type": "text_input",
          "label": "Top P",
          "tooltip": "Nucleus sampling threshold",
          "value_type": "float",
          "default": 0.9,
          "min": 0.0,
          "max": 1.0,
          "visibility": "standard"
        }
      ]
    },
    {
      "id": "triage",
      "label": "Speculative Decoding (Triage)",
      "description": "Verification options for dual-model speedups",
      "controls": [
        {
          "key": "verification_passes",
          "control_type": "stepper",
          "label": "Verification Passes",
          "tooltip": "Speculative steps evaluated per cycle",
          "value_type": "integer",
          "default": 2,
          "min": 1,
          "max": 4,
          "visibility": "advanced"
        },
        {
          "key": "draft_model",
          "control_type": "model_picker",
          "label": "Draft Model",
          "tooltip": "Choose a smaller companion model that shares the tokenizer",
          "value_type": "string",
          "filter": "same_tokenizer",
          "visibility": "standard"
        }
      ]
    }
  ]
}
```

---

## Client Dynamic Rendering Strategy

### 1. SwiftUI implementation Outline (macOS Native App)

The SwiftUI implementation replaces explicit rows with a dynamic `ForEach` loop that reads from the generated schema DTO:

```swift
import SwiftUI

// Represents a dynamic config view resolved entirely by UI Schema
struct DynamicProfileSettingsView: View {
    let schema: UISchemaDTO
    @Binding var settings: [String: AnyCodable]
    @State private var showAdvanced: Bool = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Segmented picker to toggle standard vs advanced settings
                Toggle(isOn: $showAdvanced) {
                    Text("Show Advanced & Experimental Options")
                }
                .padding(.horizontal)

                ForEach(schema.groups) { group in
                    let controls = group.controls.filter {
                        $0.visibility == .standard || showAdvanced
                    }
                    
                    if !controls.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text(group.label)
                                .font(.headline)
                            Text(group.description)
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            VStack(spacing: 8) {
                                ForEach(controls) { control in
                                    DynamicControlRow(control: control, value: binding(for: control.key))
                                }
                            }
                            .padding()
                            .background(Color(NSColor.windowBackgroundColor))
                            .cornerRadius(8)
                        }
                        .padding(.horizontal)
                    }
                }
            }
        }
    }

    private func binding(for key: String) -> Binding<AnyCodable> {
        Binding(
            get: { settings[key] ?? AnyCodable(nil) },
            set: { settings[key] = $0 }
        )
    }
}

struct DynamicControlRow: View {
    let control: UIControlSchema
    @Binding var value: AnyCodable

    var body: some View {
        HStack {
            Text(control.label)
                .frame(width: 150, alignment: .leading)
            Spacer()
            
            switch control.controlType {
            case .toggle:
                Toggle("", isOn: Binding($value, default: false))
                    .labelsHidden()
            case .text_input:
                TextField(control.label, text: Binding($value, default: ""))
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 120)
            case .slider:
                Slider(value: Binding($value, default: 0.0), in: control.min...control.max)
                    .frame(width: 200)
            case .model_picker:
                ModelPicker(selection: Binding($value, default: ""), filter: control.filter)
                    .frame(width: 200)
            case .stepper:
                Stepper(value: Binding($value, default: 0), in: control.min...control.max) {
                    Text("\(value)")
                }
            }
        }
    }
}
```

### 2. JavaScript Dashboard Implementation Outline (Web Admin Panel)

The admin panel reads the UI Schema JSON and renders controls using dynamic components or templates (e.g., in `dashboard.js` with Alpine.js or Vue.js):

```html
<template x-for="group in uiSchema.groups" :key="group.id">
  <div class="card p-4 mb-4 border rounded shadow-sm">
    <h3 class="font-bold text-lg" x-text="group.label"></h3>
    <p class="text-sm text-neutral-500 mb-3" x-text="group.description"></p>
    
    <div class="space-y-3">
      <template x-for="ctrl in group.controls" :key="ctrl.key">
        <div class="flex items-center justify-between border-b pb-2">
          <div>
            <label class="font-medium text-sm block" x-text="ctrl.label"></label>
            <span class="text-xs text-neutral-400" x-text="ctrl.tooltip"></span>
          </div>
          
          <div>
            <!-- Render Toggle -->
            <template x-if="ctrl.control_type === 'toggle'">
              <input type="checkbox" x-model="settings[ctrl.key]" class="form-checkbox">
            </template>
            
            <!-- Render Text/Numeric Input -->
            <template x-if="ctrl.control_type === 'text_input'">
              <input type="text" x-model="settings[ctrl.key]" class="form-input border rounded px-2 py-1 w-32">
            </template>
            
            <!-- Render Slider -->
            <template x-if="ctrl.control_type === 'slider'">
              <div class="flex items-center space-x-2">
                <input type="range" :min="ctrl.min" :max="ctrl.max" :step="ctrl.step" x-model="settings[ctrl.key]" class="w-48">
                <span x-text="settings[ctrl.key]" class="text-xs font-mono"></span>
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
```

---

## Future UI Wireframe Spec

The settings UI contains no hardcoded inputs except for the top-level **Execution Profile** picker. Choosing a profile fetches its specific UI schema and dynamically draws the interface.

```
+---------------------------------------------------------------------------------+
|                               MODEL SETTINGS                                    |
+---------------------------------------------------------------------------------+
|                                                                                 |
| Active Profile: [ Nemotron Speculative Triage V]   <- Selection updates schema  |
| Description: Accelerated autoregressive profile using triage draft-verification |
| Inherited From: autoregressive                                                  |
|                                                                                 |
| [ ] Show Advanced & Experimental Parameters                                     |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| | AUTOREGRESSIVE GENERATION (Capability)                                      | |
| |-----------------------------------------------------------------------------| |
| | Temperature:        [===============|===============] 0.70                 | |
| | Top P:              [ 0.90       ]                                          | |
| | Repetition Penalty: [ 1.00       ]                                          | |
| +-----------------------------------------------------------------------------+ |
|                                                                                 |
| +-----------------------------------------------------------------------------+ |
| | TRIAGE SPECULATION (Capability)                                             | |
| |-----------------------------------------------------------------------------| |
| | Verification Passes:  [ - ]  2  [ + ]                                       | |
| | Draft Model:          [ qwen-1.5b-draft-assistant.safetensors             v ] | |
| | Confidence Threshold: [===============|===============] 0.85                 | |
| +-----------------------------------------------------------------------------+ |
|                                                                                 |
|                                                     [ Save ] [ Revert Settings] |
+---------------------------------------------------------------------------------+
```
