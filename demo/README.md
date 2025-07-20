# AI-Powered Multi-Agent Recruitment System Demo

This is a Slidev presentation for demonstrating the AI-powered recruitment system in 10 minutes.

## Setup

1. Install dependencies:
```bash
# Using pnpm (recommended)
pnpm install

# Or using npm
npm install
```

2. Start the development server:
```bash
pnpm dev
# or
npm run dev
```

3. Open http://localhost:3030 in your browser

## Presentation Controls

- **Next slide**: `Space` or `→`
- **Previous slide**: `←`
- **Toggle overview**: `O`
- **Toggle presenter mode**: `P`
- **Toggle dark mode**: `D`
- **Export to PDF**: Visit http://localhost:3030/print

## Build for Production

To build the presentation for deployment:

```bash
pnpm build
# or
npm run build
```

The static files will be generated in the `dist/` directory.

## Export Options

### PDF Export
```bash
pnpm export
# or
npm run export
```

### PNG Screenshots
```bash
pnpm export --format png
```

## Structure

- `slides.md` - Main presentation content
- `pages/` - Additional slide pages
  - `appendix.md` - FAQ and additional resources
- `components/` - Vue components
  - `PresentationTimer.vue` - 10-minute countdown timer
  - `MetricsDisplay.vue` - Metrics visualization
- `styles/` - Custom CSS styles
- `public/` - Static assets (images, etc.)
- `docs/` - Additional documentation

## Customization

The presentation uses the Seriph theme with custom styling. You can modify:

- Theme in `slides.md` frontmatter
- Colors and styles in `styles/index.css`
- Components in `components/` directory
- Transitions and animations in slide frontmatter

## Tips for Presenting

1. Use presenter mode (`P`) to see notes and timer
2. The presentation timer shows remaining time out of 10 minutes
3. Slides are designed for 1920x1080 resolution
4. Test the live demo beforehand to ensure smooth operation
5. Have backup slides ready in case of technical issues