# Decentra UI Design Files

This directory contains design assets and specifications for the Decentra chat application.

## Files Included

### 1. ui-design-spec.json
A comprehensive JSON specification file containing:
- Complete color palette with all color values used in the UI
- Typography settings (fonts, sizes, weights)
- Spacing and border radius values
- Detailed component specifications for both screens (Login and Chat)
- Modal designs (Create Server, Server Settings)
- Reusable component definitions

### 2. login-screen.svg
SVG mockup of the login/authentication screen featuring:
- Centered auth box with brand colors
- Username and password input fields
- Optional invite code field
- Login and Sign Up buttons
- Proper spacing and typography

### 3. chat-screen.svg
SVG mockup of the main chat interface featuring:
- Three-column layout (Left sidebar, Middle sidebar, Main content)
- Server and DM lists in left sidebar
- Channel list in middle sidebar
- Welcome message in main chat area
- Message input at the bottom
- User section with settings menu

## How to Use These Files

### For Figma

1. **Import SVG Files**:
   - Open Figma
   - Go to File → Import
   - Select `login-screen.svg` or `chat-screen.svg`
   - The screens will be imported as vector shapes

2. **Use the JSON Specification**:
   - Use the color values in `ui-design-spec.json` to create a color palette in Figma
   - Create text styles based on the typography section
   - Create component variants for buttons, inputs, etc.
   - Reference spacing values for consistent layouts

3. **Create Design System**:
   - Create color variables from the `colorPalette` section
   - Create text styles from the `typography` section
   - Create component library from the `components` section
   - Use auto-layout with spacing values from the `spacing` section

### Editing the Design

You can edit:
- **Colors**: Update any color in the color palette section
- **Typography**: Modify font sizes, weights, or families
- **Spacing**: Adjust padding and margins
- **Components**: Add or modify button styles, inputs, etc.
- **Layouts**: Change sidebar widths, adjust component positions

### Implementing Changes

After editing in Figma:
1. Export your design specifications
2. Update the relevant values in the CSS file (`server/static/styles.css`)
3. Update HTML structure if layout changes significantly
4. Test the changes in the browser

## Design System

### Color Palette
- **Primary Brand**: #5865F2 (Discord-inspired blue)
- **Backgrounds**: Dark theme (#202225, #2f3136, #36393f)
- **Text Colors**: White (#ffffff), Light gray (#dcddde), Muted (#b9bbbe)
- **Status Colors**: Error (#f04747), Danger (#e74c3c)

### Typography
- **Font Family**: 'gg sans', 'Noto Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif
- **Headings**: 16-24px, weights 600-700
- **Body**: 14-16px, weights 400-500
- **Labels**: 12px, weight 600, uppercase

### Components
- **Buttons**: 3px border radius, 10-16px padding
- **Inputs**: Dark background, 3px border radius
- **Sidebars**: 240px width each
- **Modals**: Centered, rounded corners, shadow

## Notes

- The design follows a Discord-inspired aesthetic with dark theme
- All measurements are in pixels
- Colors use hex values and rgba for transparency
- The layout is responsive and uses flexbox
- Accessibility considerations include proper contrast ratios

## Questions?

If you have questions about the design or need modifications, please refer to the JSON specification file for detailed component properties and values.
