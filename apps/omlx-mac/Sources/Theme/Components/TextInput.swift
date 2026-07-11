import SwiftUI

struct TextInput: View {
    @Binding var text: String
    var titleKey: LocalizedStringKey
    var placeholder: String
    var isSecure: Bool
    var mono: Bool
    var isNumeric: Bool
    var range: ClosedRange<Double>?
    var step: Double?
    var suffix: String?
    var width: CGFloat?

    @FocusState private var isFocused: Bool
    @Environment(\.omlxTheme) private var theme
    @Environment(\.omlxPageRole) private var pageRole

    init(_ titleKey: LocalizedStringKey = "", text: Binding<String>, placeholder: String = "", isSecure: Bool = false, mono: Bool = false, isNumeric: Bool = false, range: ClosedRange<Double>? = nil, step: Double? = nil, suffix: String? = nil, width: CGFloat? = nil) {
        self._text = text
        self.titleKey = titleKey
        self.placeholder = placeholder
        self.isSecure = isSecure
        self.mono = mono
        self.isNumeric = isNumeric
        self.range = range
        self.step = step
        self.suffix = suffix
        self.width = width
    }

    private var textAsDouble: Binding<Double> {
        Binding(
            get: { Double(text) ?? 0 },
            set: { text = $0.formatted(.number.grouping(.never)) }
        )
    }

    var body: some View {
        let atmosphere = OneDesign.SemanticRoles.resolveAtmosphere(for: pageRole, isDark: theme.isDark)
        let strokeColor: Color = {
            if isFocused {
                return atmosphere.accent
            } else {
                return theme.inputBorder
            }
        }()
        
        let shadowColor: Color = {
            if isFocused {
                return atmosphere.glowColor
            } else {
                return .clear
            }
        }()
        
        return HStack(spacing: 0) {
            field
                .textFieldStyle(.plain)
                .font(mono ? OneDesign.Typography.omlxCode() : OneDesign.Typography.omlxBody())
                .focused($isFocused)
                .foregroundStyle(theme.text)
            
            HStack(spacing: 0) {
                if let suffix {
                    Text(suffix)
                        .font(OneDesign.Typography.omlxCaption())
                        .foregroundStyle(theme.textSecondary)
                        .padding(.horizontal, OneDesign.Spacing.spacingS)
                }
                if isNumeric {
                    stepper
                }
            }
        }
        .padding(.horizontal, OneDesign.Spacing.spacingS)
        .padding(.vertical, 5)
        .frame(height: 28)
        .background(theme.inputBg)
        .clipShape(RoundedRectangle(cornerRadius: OneDesign.Layout.controlRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: OneDesign.Layout.controlRadius, style: .continuous)
                .stroke(strokeColor, lineWidth: isFocused ? 1.2 : 0.8)
        )
        .shadow(color: shadowColor, radius: isFocused ? 3 : 0)
        .animation(OneDesign.Motion.fast, value: isFocused)
        .frame(maxWidth: width)
    }

    private var field: some View {
        Group {
            if isSecure {
                SecureField(titleKey, text: $text, prompt: Text(placeholder).foregroundColor(theme.textTertiary))
            } else {
                TextField(titleKey, text: $text, prompt: Text(placeholder).foregroundColor(theme.textTertiary))
            }
        }
    }

    private var stepper: some View {
        Group {
            switch (range, step) {
            case let (range?, step?):
                Stepper(titleKey, value: textAsDouble, in: range, step: step)
            case let (range?, nil):
                Stepper(titleKey, value: textAsDouble, in: range)
            default:
                Stepper(titleKey, value: textAsDouble)
            }
        }
        .labelsHidden()
        .controlSize(.small)
        .padding(.trailing, 1)
    }
}
