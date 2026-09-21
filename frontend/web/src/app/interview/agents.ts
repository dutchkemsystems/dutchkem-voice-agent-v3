export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  specialties: string[];
}

export const INTERVIEW_AGENTS: AgentInfo[] = [
  {
    id: "hr",
    name: "HR Agent",
    description: "Handles behavioral questions, culture fit, and workplace scenarios.",
    icon: "👥",
    specialties: ["Behavioral", "Culture Fit", "Workplace Ethics"],
  },
  {
    id: "manager",
    name: "Manager Agent",
    description: "Leadership, team management, and strategic decision questions.",
    icon: "📋",
    specialties: ["Leadership", "Strategy", "Decision Making"],
  },
  {
    id: "technical",
    name: "Technical Agent",
    description: "System design, architecture, and technical concept questions.",
    icon: "⚙️",
    specialties: ["System Design", "Architecture", "Technical Concepts"],
  },
  {
    id: "coding",
    name: "Coding Agent",
    description: "Live coding, algorithms, data structures, and code review.",
    icon: "💻",
    specialties: ["Algorithms", "Data Structures", "Code Review"],
  },
  {
    id: "client_meeting",
    name: "Client Meeting Agent",
    description: "Client presentations, stakeholder communication, and demos.",
    icon: "🤝",
    specialties: ["Presentations", "Stakeholder Comms", "Demos"],
  },
  {
    id: "mentoring",
    name: "Mentoring Agent",
    description: "Coaching, knowledge transfer, and junior developer guidance.",
    icon: "🎯",
    specialties: ["Coaching", "Knowledge Transfer", "Guidance"],
  },
  {
    id: "performance_review",
    name: "Performance Review Agent",
    description: "Self-assessment, feedback delivery, and goal setting.",
    icon: "📊",
    specialties: ["Self-Assessment", "Feedback", "Goal Setting"],
  },
  {
    id: "board_presentation",
    name: "Board Presentation Agent",
    description: "Executive summaries, KPI reporting, and boardroom communication.",
    icon: "🏛️",
    specialties: ["Executive Summary", "KPIs", "Board Communication"],
  },
  {
    id: "sales",
    name: "Sales Agent",
    description: "Sales pitches, objection handling, and negotiation scenarios.",
    icon: "💰",
    specialties: ["Sales Pitches", "Objection Handling", "Negotiation"],
  },
  {
    id: "training",
    name: "Training Agent",
    description: "Onboarding, skill assessment, and learning path guidance.",
    icon: "📚",
    specialties: ["Onboarding", "Skill Assessment", "Learning Paths"],
  },
  {
    id: "internal_comms",
    name: "Internal Comms Agent",
    description: "Team updates, cross-functional communication, and async messaging.",
    icon: "💬",
    specialties: ["Team Updates", "Cross-functional", "Async Comms"],
  },
  {
    id: "customer_support",
    name: "Customer Support Agent",
    description: "Ticket triage, customer empathy, and resolution communication.",
    icon: "🎧",
    specialties: ["Ticket Triage", "Customer Empathy", "Resolution"],
  },
];
