# ✨ Prompt Builder

A stunning, interactive web application that helps users construct high-quality AI prompts through a guided wizard interface.

## Features

### 🎨 Visual Design
- **Immersive 3D design language** with floating glass panels and subtle parallax effects
- **Animated gradient orbs and particles** in the background
- **Premium dark theme** with vibrant accent gradients (violet/cyan/electric blue)
- **Glassmorphism cards** with soft shadows and depth
- **Smooth micro-interactions** on hover/click with fluid transitions

### 🧙 Step-by-Step Wizard
1. **Goal** - Define your primary objective
2. **Role/Persona** - Choose the AI's expertise area
3. **Context** - Provide background information
4. **Format** - Select output format (paragraph, bullet points, code, etc.)
5. **Constraints** - Set specific requirements
6. **Tone** - Choose the writing style

### 📊 Core Features
- **Live Preview Panel** - See your generated prompt update in real-time
- **Template Gallery** - Quick-start templates for coding, marketing, writing, research, and more
- **Prompt Quality Score** - Real-time scoring for clarity, specificity, and structure
- **Copy to Clipboard** - One-click copy functionality
- **Export Options** - Download as .txt or .md files
- **Save/Load Prompts** - Store prompts locally in browser storage

### ♿ Accessibility
- WCAG AA compliant
- Full keyboard navigation support
- Screen reader friendly with ARIA labels
- Reduced motion support for users who prefer it

### 📱 Responsive Design
- Fully responsive layout for desktop, tablet, and mobile
- Adaptive grid system
- Touch-friendly controls

## Tech Stack
- **Vite** - Build tool and dev server
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Custom properties, animations, glassmorphism effects
- **LocalStorage API** - For saving prompts locally

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to the project directory
cd prompt-builder

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Usage

1. Open the application in your browser
2. Follow the wizard steps to build your prompt:
   - Enter your goal/objective
   - Select or customize a role/persona
   - Add relevant context
   - Choose an output format
   - Set any constraints
   - Select a tone
3. Watch the live preview update as you go
4. Use the quality score to improve your prompt
5. Copy, export, or save your finished prompt

### Templates

The app includes 12 pre-built templates across categories:
- **Coding**: Code Review, API Documentation
- **Marketing**: Social Media Campaign, Email Sequence
- **Writing**: Blog Post Outline, Story Development
- **Research**: Market Analysis, Literature Review
- **Business**: Business Plan, SWOT Analysis
- **Learning**: Study Guide, Skill Learning Path

## Project Structure

```
prompt-builder/
├── index.html          # Main HTML file with embedded CSS
├── src/
│   └── main.js         # Application logic
├── public/             # Static assets
├── dist/               # Production build output
├── package.json        # Dependencies and scripts
├── vite.config.js      # Vite configuration
└── README.md           # This file
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT License - feel free to use this project for personal or commercial purposes.

---

Built with ❤️ for crafting better AI prompts
