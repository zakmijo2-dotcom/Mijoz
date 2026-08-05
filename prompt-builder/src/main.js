// Prompt Builder - Main Application Logic

// State management
const state = {
  currentStep: 0,
  totalSteps: 6,
  data: {
    goal: '',
    role: '',
    roleCustom: '',
    context: '',
    format: '',
    formatCustom: '',
    constraints: '',
    length: '',
    tone: '',
    toneCustom: ''
  },
  savedPrompts: []
};

// Role descriptions for prompt generation
const roleDescriptions = {
  'software-engineer': 'an experienced software engineer with expertise in best practices, clean code, and scalable architecture',
  'marketing-expert': 'a seasoned marketing expert with deep knowledge of digital marketing strategies, customer acquisition, and brand building',
  'content-writer': 'a professional content writer skilled in creating engaging, clear, and compelling copy',
  'data-scientist': 'a data scientist with expertise in statistical analysis, machine learning, and data visualization',
  'business-consultant': 'a business consultant with experience in strategy development, operational efficiency, and growth planning',
  'creative-designer': 'a creative designer with a keen eye for aesthetics, user experience, and visual storytelling',
  'research-analyst': 'a research analyst skilled in gathering, analyzing, and synthesizing information from multiple sources',
  'educator': 'an experienced educator who excels at explaining complex concepts in accessible ways',
  'legal-advisor': 'a legal advisor with knowledge of regulations, compliance, and risk management',
  'health-coach': 'a health and wellness coach focused on holistic well-being and sustainable lifestyle changes'
};

// Format instructions
const formatInstructions = {
  'paragraph': 'Provide your response in well-structured paragraphs.',
  'bullet-points': 'Present your response as bullet points for easy scanning.',
  'numbered-list': 'Organize your response as a numbered list.',
  'table': 'Format your response as a table where appropriate.',
  'code': 'Provide your response as code with proper syntax and comments.',
  'step-by-step': 'Break down your response into clear, sequential steps.',
  'json': 'Format your response as valid JSON.',
  'markdown': 'Use Markdown formatting with appropriate headings, lists, and emphasis.'
};

// Tone descriptors
const toneDescriptors = {
  'professional': 'Maintain a professional and formal tone throughout.',
  'casual': 'Use a casual, conversational tone.',
  'friendly': 'Write in a friendly and approachable manner.',
  'authoritative': 'Adopt an authoritative and confident tone.',
  'encouraging': 'Be encouraging and supportive in your response.',
  'humorous': 'Incorporate appropriate humor while remaining helpful.',
  'technical': 'Use technical language appropriate for experts in the field.',
  'creative': 'Employ creative and imaginative language.'
};

// Templates
const templates = [
  {
    category: 'Coding',
    name: 'Code Review Request',
    preview: 'Review my code for bugs, performance issues, and best practices...',
    data: {
      goal: 'I need a thorough code review to identify potential bugs, performance bottlenecks, security vulnerabilities, and areas for improvement following best practices.',
      role: 'software-engineer',
      context: 'This is production code that will be used by thousands of users. Performance and security are critical.',
      format: 'bullet-points',
      formatCustom: 'Group feedback by category (bugs, performance, security, style)',
      constraints: 'Focus on high-impact issues first. Provide specific code examples for fixes.',
      length: 'detailed',
      tone: 'professional'
    }
  },
  {
    category: 'Coding',
    name: 'API Documentation',
    preview: 'Generate comprehensive API documentation with examples...',
    data: {
      goal: 'Create comprehensive API documentation that developers can use to integrate with our service quickly and effectively.',
      role: 'software-engineer',
      context: 'REST API for a project management tool. Target audience is frontend and backend developers.',
      format: 'markdown',
      formatCustom: 'Include endpoint descriptions, request/response examples, authentication details, and error codes',
      constraints: 'Make it beginner-friendly but include advanced usage examples. Keep examples realistic.',
      length: 'extended',
      tone: 'technical'
    }
  },
  {
    category: 'Marketing',
    name: 'Social Media Campaign',
    preview: 'Create a multi-platform social media campaign strategy...',
    data: {
      goal: 'Develop a comprehensive social media campaign to launch our new product and generate buzz among our target audience.',
      role: 'marketing-expert',
      context: 'B2C SaaS product targeting millennials and Gen Z. Budget is moderate. Launch date is in 4 weeks.',
      format: 'step-by-step',
      formatCustom: 'Include platform-specific strategies, content ideas, posting schedules, and KPIs',
      constraints: 'Focus on organic growth strategies with some paid advertising recommendations. Include timeline.',
      length: 'detailed',
      tone: 'creative'
    }
  },
  {
    category: 'Marketing',
    name: 'Email Sequence',
    preview: 'Write a welcome email sequence for new subscribers...',
    data: {
      goal: 'Create an engaging 5-email welcome sequence that nurtures new subscribers and guides them toward becoming customers.',
      role: 'content-writer',
      context: 'Online course platform teaching digital marketing. Audience is aspiring marketers and entrepreneurs.',
      format: 'markdown',
      formatCustom: 'Include subject lines, preview text, and full email body for each email in the sequence',
      constraints: 'Each email should have a clear CTA. Build value before selling. Keep emails under 300 words.',
      length: 'medium',
      tone: 'friendly'
    }
  },
  {
    category: 'Writing',
    name: 'Blog Post Outline',
    preview: 'Generate a detailed blog post outline with key points...',
    data: {
      goal: 'Create a comprehensive blog post outline that covers all essential aspects of the topic and provides value to readers.',
      role: 'content-writer',
      context: 'Blog about productivity and time management for remote workers. SEO-optimized content needed.',
      format: 'numbered-list',
      formatCustom: 'Include H2 and H3 headings, key points under each section, and suggested word counts',
      constraints: 'Structure for skimmability. Include introduction hooks and conclusion takeaways. Suggest internal linking opportunities.',
      length: 'detailed',
      tone: 'professional'
    }
  },
  {
    category: 'Writing',
    name: 'Story Development',
    preview: 'Help develop characters, plot, and world-building...',
    data: {
      goal: 'Help me develop compelling characters, an engaging plot structure, and rich world-building for my science fiction novel.',
      role: 'creative-designer',
      context: 'First-time novelist writing a space opera. Looking for fresh ideas while avoiding common tropes.',
      format: 'bullet-points',
      formatCustom: 'Separate sections for character profiles, plot outline, and world-building elements',
      constraints: 'Provide thought-provoking questions to help me develop my own ideas. Include examples from successful works.',
      length: 'extended',
      tone: 'encouraging'
    }
  },
  {
    category: 'Research',
    name: 'Market Analysis',
    preview: 'Conduct a comprehensive market analysis framework...',
    data: {
      goal: 'Provide a structured framework for analyzing market size, competition, trends, and opportunities in a specific industry.',
      role: 'research-analyst',
      context: 'Evaluating entry into the electric vehicle charging station market in Southeast Asia.',
      format: 'table',
      formatCustom: 'Include frameworks, key metrics to track, data sources, and analysis methods',
      constraints: 'Make it actionable. Include both quantitative and qualitative analysis approaches.',
      length: 'detailed',
      tone: 'professional'
    }
  },
  {
    category: 'Research',
    name: 'Literature Review',
    preview: 'Structure a literature review for academic research...',
    data: {
      goal: 'Help me structure and write a comprehensive literature review that synthesizes existing research and identifies gaps.',
      role: 'research-analyst',
      context: 'Graduate thesis on the impact of AI on workplace productivity. Need to cover papers from the last 10 years.',
      format: 'markdown',
      formatCustom: 'Include thematic organization, synthesis techniques, and citation management tips',
      constraints: 'Emphasize critical analysis over summary. Show how to identify research gaps.',
      length: 'extended',
      tone: 'technical'
    }
  },
  {
    category: 'Business',
    name: 'Business Plan',
    preview: 'Create a lean startup business plan template...',
    data: {
      goal: 'Generate a lean business plan that covers all essential elements for a startup seeking seed funding.',
      role: 'business-consultant',
      context: 'Tech startup developing an AI-powered customer service solution. Targeting angel investors.',
      format: 'step-by-step',
      formatCustom: 'Include executive summary, problem/solution, market analysis, business model, team, and financial projections',
      constraints: 'Keep it concise but comprehensive. Focus on what investors care about most.',
      length: 'detailed',
      tone: 'professional'
    }
  },
  {
    category: 'Business',
    name: 'SWOT Analysis',
    preview: 'Perform a detailed SWOT analysis framework...',
    data: {
      goal: 'Create a thorough SWOT analysis framework to evaluate strategic positioning and identify opportunities.',
      role: 'business-consultant',
      context: 'Established retail company considering expansion into e-commerce. Facing increased online competition.',
      format: 'table',
      formatCustom: 'Include specific examples in each quadrant and strategic recommendations based on findings',
      constraints: 'Make it actionable. Connect strengths to opportunities and address weaknesses strategically.',
      length: 'medium',
      tone: 'authoritative'
    }
  },
  {
    category: 'Learning',
    name: 'Study Guide',
    preview: 'Create a comprehensive study guide for exam preparation...',
    data: {
      goal: 'Develop an effective study guide that helps students master key concepts and prepare thoroughly for exams.',
      role: 'educator',
      context: 'University-level computer science course on algorithms and data structures. Final exam in 3 weeks.',
      format: 'numbered-list',
      formatCustom: 'Include key topics, study techniques, practice problems, and self-assessment questions',
      constraints: 'Prioritize high-yield topics. Include memory techniques and test-taking strategies.',
      length: 'detailed',
      tone: 'encouraging'
    }
  },
  {
    category: 'Learning',
    name: 'Skill Learning Path',
    preview: 'Design a structured learning path for acquiring a new skill...',
    data: {
      goal: 'Create a structured learning path that takes someone from beginner to competent in a new skill efficiently.',
      role: 'educator',
      context: 'Adult learner wanting to transition into UX design career. Can dedicate 10 hours per week.',
      format: 'step-by-step',
      formatCustom: 'Include phases, resources, projects, milestones, and estimated timelines',
      constraints: 'Balance theory with hands-on practice. Include portfolio-building projects. Recommend free and paid resources.',
      length: 'extended',
      tone: 'encouraging'
    }
  }
];

// DOM Elements
const elements = {};

// Initialize the application
function init() {
  cacheElements();
  loadSavedPrompts();
  renderTemplates();
  renderSavedPrompts();
  updatePreview();
  setupEventListeners();
  createParticles();
}

// Cache DOM elements
function cacheElements() {
  elements.steps = document.querySelectorAll('.step-content');
  elements.indicators = document.querySelectorAll('.step-indicator');
  elements.labels = document.querySelectorAll('.step-label');
  elements.prevBtn = document.getElementById('prev-btn');
  elements.nextBtn = document.getElementById('next-btn');
  elements.previewContent = document.getElementById('preview-content');
  elements.qualityScore = document.getElementById('quality-score');
  elements.clarityScore = document.getElementById('clarity-score');
  elements.specificityScore = document.getElementById('specificity-score');
  elements.structureScore = document.getElementById('structure-score');
  elements.copyBtn = document.getElementById('copy-btn');
  elements.exportTxtBtn = document.getElementById('export-txt-btn');
  elements.exportMdBtn = document.getElementById('export-md-btn');
  elements.saveBtn = document.getElementById('save-btn');
  elements.templateGrid = document.getElementById('template-grid');
  elements.savedList = document.getElementById('saved-list');
  elements.toast = document.getElementById('toast');
  
  // Form fields
  elements.goal = document.getElementById('goal');
  elements.roleSelect = document.getElementById('role-select');
  elements.roleCustom = document.getElementById('role-custom');
  elements.context = document.getElementById('context');
  elements.formatCustom = document.getElementById('format-custom');
  elements.constraints = document.getElementById('constraints');
  elements.length = document.getElementById('length');
  elements.toneCustom = document.getElementById('tone-custom');
}

// Setup event listeners
function setupEventListeners() {
  // Navigation buttons
  elements.prevBtn.addEventListener('click', () => goToStep(state.currentStep - 1));
  elements.nextBtn.addEventListener('click', () => goToStep(state.currentStep + 1));
  
  // Step indicators (keyboard navigation)
  elements.indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => goToStep(index));
    indicator.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        goToStep(index);
      }
    });
  });
  
  // Form inputs - update preview on change
  const formInputs = [
    elements.goal,
    elements.roleSelect,
    elements.roleCustom,
    elements.context,
    elements.constraints,
    elements.length,
    elements.formatCustom,
    elements.toneCustom
  ];
  
  formInputs.forEach(input => {
    input.addEventListener('input', () => {
      updateStateFromForm();
      updatePreview();
    });
  });
  
  // Option cards (format and tone)
  document.querySelectorAll('.option-card').forEach(card => {
    card.addEventListener('click', () => selectOption(card));
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectOption(card);
      }
    });
  });
  
  // Action buttons
  elements.copyBtn.addEventListener('click', copyToClipboard);
  elements.exportTxtBtn.addEventListener('click', () => exportPrompt('txt'));
  elements.exportMdBtn.addEventListener('click', () => exportPrompt('md'));
  elements.saveBtn.addEventListener('click', savePrompt);
  
  // Keyboard navigation
  document.addEventListener('keydown', handleKeyboardNavigation);
}

// Handle keyboard navigation
function handleKeyboardNavigation(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
    return;
  }
  
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault();
    if (state.currentStep < state.totalSteps - 1) {
      goToStep(state.currentStep + 1);
    }
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault();
    if (state.currentStep > 0) {
      goToStep(state.currentStep - 1);
    }
  }
}

// Go to specific step
function goToStep(stepIndex) {
  if (stepIndex < 0 || stepIndex >= state.totalSteps) return;
  
  // Validate current step before moving forward
  if (stepIndex > state.currentStep && !validateStep(state.currentStep)) {
    showToast('Please fill in the required fields before continuing', 'warning');
    return;
  }
  
  state.currentStep = stepIndex;
  
  // Update step content visibility
  elements.steps.forEach((step, index) => {
    step.classList.toggle('active', index === stepIndex);
  });
  
  // Update indicators
  elements.indicators.forEach((indicator, index) => {
    indicator.classList.toggle('active', index === stepIndex);
    indicator.classList.toggle('completed', index < stepIndex);
    indicator.setAttribute('aria-selected', index === stepIndex);
    indicator.setAttribute('tabindex', index === stepIndex ? '0' : '-1');
  });
  
  // Update labels
  elements.labels.forEach((label, index) => {
    label.classList.toggle('active', index === stepIndex);
    label.classList.toggle('completed', index < stepIndex);
  });
  
  // Update buttons
  elements.prevBtn.disabled = stepIndex === 0;
  elements.nextBtn.textContent = stepIndex === state.totalSteps - 1 ? 'Finish ✓' : 'Next →';
  
  // Scroll to top of wizard on mobile
  if (window.innerWidth < 768) {
    document.querySelector('.wizard-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// Validate current step
function validateStep(stepIndex) {
  switch (stepIndex) {
    case 0: // Goal
      return state.data.goal.trim().length > 0;
    case 1: // Role
      return true; // Role is optional (has defaults)
    case 2: // Context
      return true; // Context is optional
    case 3: // Format
      return true; // Format has defaults
    case 4: // Constraints
      return true; // Constraints are optional
    case 5: // Tone
      return true; // Tone has defaults
    default:
      return true;
  }
}

// Select option card
function selectOption(card) {
  const parent = card.parentElement;
  const type = card.dataset.format ? 'format' : 'tone';
  const value = card.dataset.format || card.dataset.tone;
  
  // Deselect siblings
  parent.querySelectorAll('.option-card').forEach(c => {
    c.classList.remove('selected');
    c.setAttribute('aria-checked', 'false');
  });
  
  // Select clicked card
  card.classList.add('selected');
  card.setAttribute('aria-checked', 'true');
  
  // Update state
  if (type === 'format') {
    state.data.format = value;
  } else {
    state.data.tone = value;
  }
  
  updatePreview();
}

// Update state from form
function updateStateFromForm() {
  state.data.goal = elements.goal.value;
  state.data.role = elements.roleSelect.value;
  state.data.roleCustom = elements.roleCustom.value;
  state.data.context = elements.context.value;
  state.data.formatCustom = elements.formatCustom.value;
  state.data.constraints = elements.constraints.value;
  state.data.length = elements.length.value;
  state.data.toneCustom = elements.toneCustom.value;
}

// Generate the prompt
function generatePrompt() {
  const parts = [];
  
  // Role/Persona
  let roleText = '';
  if (state.data.roleCustom) {
    roleText = state.data.roleCustom;
  } else if (state.data.role && roleDescriptions[state.data.role]) {
    roleText = roleDescriptions[state.data.role];
  }
  
  if (roleText) {
    parts.push(`Act as ${roleText}.`);
  }
  
  // Goal
  if (state.data.goal) {
    parts.push(`\n${state.data.goal}`);
  }
  
  // Context
  if (state.data.context) {
    parts.push(`\nContext: ${state.data.context}`);
  }
  
  // Format
  if (state.data.format && formatInstructions[state.data.format]) {
    parts.push(`\n${formatInstructions[state.data.format]}`);
    if (state.data.formatCustom) {
      parts.push(` Additional format requirements: ${state.data.formatCustom}`);
    }
  } else if (state.data.formatCustom) {
    parts.push(`\nFormat requirements: ${state.data.formatCustom}`);
  }
  
  // Constraints
  if (state.data.constraints) {
    parts.push(`\nConstraints: ${state.data.constraints}`);
  }
  
  // Length
  if (state.data.length) {
    const lengthMap = {
      'brief': 'Keep your response brief (1-2 paragraphs).',
      'medium': 'Provide a medium-length response (3-5 paragraphs).',
      'detailed': 'Provide a detailed and comprehensive response.',
      'extended': 'Provide an extended, in-depth analysis.'
    };
    parts.push(`\n${lengthMap[state.data.length]}`);
  }
  
  // Tone
  if (state.data.tone && toneDescriptors[state.data.tone]) {
    parts.push(`\n${toneDescriptors[state.data.tone]}`);
    if (state.data.toneCustom) {
      parts.push(` ${state.data.toneCustom}`);
    }
  } else if (state.data.toneCustom) {
    parts.push(`\nTone notes: ${state.data.toneCustom}`);
  }
  
  return parts.join('').trim();
}

// Calculate quality score
function calculateQualityScore() {
  let clarity = 0;
  let specificity = 0;
  let structure = 0;
  
  // Clarity score (based on goal completeness)
  const goalLength = state.data.goal.trim().length;
  if (goalLength > 0) clarity += 30;
  if (goalLength > 50) clarity += 20;
  if (goalLength > 100) clarity += 20;
  if (state.data.goal.includes('.') && state.data.goal.split('.').length > 2) clarity += 30;
  
  // Specificity score (based on context and constraints)
  if (state.data.context.trim().length > 0) specificity += 30;
  if (state.data.context.trim().length > 100) specificity += 20;
  if (state.data.constraints.trim().length > 0) specificity += 25;
  if (state.data.constraints.trim().length > 50) specificity += 25;
  
  // Structure score (based on format, role, and tone selection)
  if (state.data.role || state.data.roleCustom) structure += 20;
  if (state.data.format) structure += 25;
  if (state.data.tone) structure += 20;
  if (state.data.length) structure += 15;
  if (state.data.formatCustom || state.data.toneCustom) structure += 20;
  
  const total = Math.round((clarity + specificity + structure) / 3);
  
  return {
    clarity: Math.min(100, clarity),
    specificity: Math.min(100, specificity),
    structure: Math.min(100, structure),
    total
  };
}

// Update preview panel
function updatePreview() {
  const prompt = generatePrompt();
  const scores = calculateQualityScore();
  
  // Update preview content
  if (prompt) {
    elements.previewContent.textContent = prompt;
    elements.previewContent.classList.add('has-text');
  } else {
    elements.previewContent.innerHTML = '<span class="preview-placeholder">Your generated prompt will appear here as you fill out the wizard...</span>';
    elements.previewContent.classList.remove('has-text');
  }
  
  // Update scores
  elements.qualityScore.textContent = prompt ? scores.total : 0;
  elements.clarityScore.textContent = scores.clarity > 0 ? scores.clarity : '-';
  elements.specificityScore.textContent = scores.specificity > 0 ? scores.specificity : '-';
  elements.structureScore.textContent = scores.structure > 0 ? scores.structure : '-';
}

// Copy to clipboard
async function copyToClipboard() {
  const prompt = generatePrompt();
  if (!prompt) {
    showToast('Nothing to copy yet!', 'warning');
    return;
  }
  
  try {
    await navigator.clipboard.writeText(prompt);
    showToast('Prompt copied to clipboard!', 'success');
  } catch (err) {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = prompt;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showToast('Prompt copied to clipboard!', 'success');
  }
}

// Export prompt
function exportPrompt(format) {
  const prompt = generatePrompt();
  if (!prompt) {
    showToast('Nothing to export yet!', 'warning');
    return;
  }
  
  const filename = `prompt-${new Date().toISOString().split('T')[0]}.${format}`;
  const mimeType = format === 'md' ? 'text/markdown' : 'text/plain';
  
  const blob = new Blob([prompt], { type: mimeType });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  showToast(`Exported as ${filename}`, 'success');
}

// Save prompt
function savePrompt() {
  const prompt = generatePrompt();
  if (!prompt) {
    showToast('Nothing to save yet!', 'warning');
    return;
  }
  
  const savedItem = {
    id: Date.now(),
    date: new Date().toISOString(),
    prompt: prompt,
    data: { ...state.data }
  };
  
  state.savedPrompts.unshift(savedItem);
  
  // Limit to 20 saved prompts
  if (state.savedPrompts.length > 20) {
    state.savedPrompts.pop();
  }
  
  localStorage.setItem('savedPrompts', JSON.stringify(state.savedPrompts));
  renderSavedPrompts();
  showToast('Prompt saved successfully!', 'success');
}

// Load saved prompts from localStorage
function loadSavedPrompts() {
  const stored = localStorage.getItem('savedPrompts');
  if (stored) {
    try {
      state.savedPrompts = JSON.parse(stored);
    } catch (e) {
      state.savedPrompts = [];
    }
  }
}

// Render saved prompts list
function renderSavedPrompts() {
  if (state.savedPrompts.length === 0) {
    elements.savedList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">No saved prompts yet. Create and save your first prompt!</p>';
    return;
  }
  
  elements.savedList.innerHTML = state.savedPrompts.map(item => {
    const date = new Date(item.date).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    const preview = item.prompt.substring(0, 80) + (item.prompt.length > 80 ? '...' : '');
    
    return `
      <div class="saved-item" data-id="${item.id}">
        <div class="saved-item-info">
          <div class="saved-item-date">${date}</div>
          <div class="saved-item-preview">${escapeHtml(preview)}</div>
        </div>
        <div class="saved-item-actions">
          <button class="btn-icon load-prompt" title="Load prompt" aria-label="Load this prompt">
            📥
          </button>
          <button class="btn-icon delete" title="Delete prompt" aria-label="Delete this prompt">
            🗑️
          </button>
        </div>
      </div>
    `;
  }).join('');
  
  // Add event listeners to saved items
  elements.savedList.querySelectorAll('.saved-item').forEach(item => {
    const id = parseInt(item.dataset.id);
    const savedItem = state.savedPrompts.find(p => p.id === id);
    
    item.querySelector('.load-prompt').addEventListener('click', (e) => {
      e.stopPropagation();
      loadPrompt(savedItem);
    });
    
    item.querySelector('.delete').addEventListener('click', (e) => {
      e.stopPropagation();
      deletePrompt(id);
    });
    
    item.addEventListener('click', () => loadPrompt(savedItem));
  });
}

// Load a saved prompt
function loadPrompt(savedItem) {
  state.data = { ...savedItem.data };
  
  // Update form fields
  elements.goal.value = state.data.goal || '';
  elements.roleSelect.value = state.data.role || '';
  elements.roleCustom.value = state.data.roleCustom || '';
  elements.context.value = state.data.context || '';
  elements.formatCustom.value = state.data.formatCustom || '';
  elements.constraints.value = state.data.constraints || '';
  elements.length.value = state.data.length || '';
  elements.toneCustom.value = state.data.toneCustom || '';
  
  // Update option cards
  document.querySelectorAll('.option-card').forEach(card => {
    const format = card.dataset.format;
    const tone = card.dataset.tone;
    
    card.classList.remove('selected');
    card.setAttribute('aria-checked', 'false');
    
    if (format && format === state.data.format) {
      card.classList.add('selected');
      card.setAttribute('aria-checked', 'true');
    }
    if (tone && tone === state.data.tone) {
      card.classList.add('selected');
      card.setAttribute('aria-checked', 'true');
    }
  });
  
  goToStep(0);
  updatePreview();
  showToast('Prompt loaded successfully!', 'success');
}

// Delete a saved prompt
function deletePrompt(id) {
  state.savedPrompts = state.savedPrompts.filter(p => p.id !== id);
  localStorage.setItem('savedPrompts', JSON.stringify(state.savedPrompts));
  renderSavedPrompts();
  showToast('Prompt deleted', 'success');
}

// Render templates
function renderTemplates() {
  elements.templateGrid.innerHTML = templates.map((template, index) => `
    <div class="template-card" data-template="${index}">
      <div class="template-category">${template.category}</div>
      <div class="template-name">${template.name}</div>
      <div class="template-preview">${template.preview}</div>
    </div>
  `).join('');
  
  // Add click handlers
  elements.templateGrid.querySelectorAll('.template-card').forEach(card => {
    card.addEventListener('click', () => {
      const index = parseInt(card.dataset.template);
      loadTemplate(templates[index]);
    });
  });
}

// Load a template
function loadTemplate(template) {
  state.data = { ...template.data };
  
  // Update form fields
  elements.goal.value = state.data.goal || '';
  elements.roleSelect.value = state.data.role || '';
  elements.roleCustom.value = state.data.roleCustom || '';
  elements.context.value = state.data.context || '';
  elements.formatCustom.value = state.data.formatCustom || '';
  elements.constraints.value = state.data.constraints || '';
  elements.length.value = state.data.length || '';
  elements.toneCustom.value = state.data.toneCustom || '';
  
  // Update option cards
  document.querySelectorAll('.option-card').forEach(card => {
    const format = card.dataset.format;
    const tone = card.dataset.tone;
    
    card.classList.remove('selected');
    card.setAttribute('aria-checked', 'false');
    
    if (format && format === state.data.format) {
      card.classList.add('selected');
      card.setAttribute('aria-checked', 'true');
    }
    if (tone && tone === state.data.tone) {
      card.classList.add('selected');
      card.setAttribute('aria-checked', 'true');
    }
  });
  
  goToStep(0);
  updatePreview();
  showToast('Template loaded! Customize as needed.', 'success');
}

// Show toast notification
function showToast(message, type = 'success') {
  const toastMessage = elements.toast.querySelector('.toast-message');
  toastMessage.textContent = message;
  
  elements.toast.classList.add('show');
  
  setTimeout(() => {
    elements.toast.classList.remove('show');
  }, 3000);
}

// Create floating particles
function createParticles() {
  const container = document.getElementById('particles');
  const particleCount = 30;
  
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.animationDelay = `${Math.random() * 15}s`;
    particle.style.animationDuration = `${15 + Math.random() * 10}s`;
    particle.style.opacity = Math.random() * 0.3 + 0.1;
    
    // Random color variation
    const colors = ['#8b5cf6', '#06b6d4', '#3b82f6'];
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    
    container.appendChild(particle);
  }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
