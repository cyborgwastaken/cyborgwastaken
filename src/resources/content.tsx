import { About, Blog, Gallery, Home, Newsletter, Person, Social, Work } from "@/types";
import { Line, Row, Text } from "@once-ui-system/core";

const person: Person = {
  firstName: "Ayushman",
  lastName: "Das",
  name: `Ayushman Das`,
  dob: new Date(2005, 3, 22),
  role: "Backend & Platform Reliability Engineer",
  avatar: "/images/avatar.jpg",
  email: "ayushmandas.dudul@gmail.com",
  location: "Asia/Kolkata", // Expecting the IANA time zone identifier, e.g., 'Europe/Vienna'
  city: "Bhubaneshwar",
  state: "Odisha",
  country: "India",
  continent: "Asia",
  languages: ["English", "Hindi"], // optional: Leave the array empty if you don't want to display languages
  locale: "en", // BCP 47 language tag for the HTML lang attribute, e.g., 'en', 'ja', 'zh-TW'
};

const newsletter: Newsletter = {
  display: true,
  title: <>Subscribe to {person.firstName}'s Newsletter</>,
  description: <>My weekly newsletter about creativity and engineering</>,
};

const social: Social = [
  // Links are automatically displayed.
  // Import new icons in /once-ui/icons.ts
  // Set essentials: true for links you want to show on the about page
  {
    name: "GitHub",
    icon: "github",
    link: "https://github.com/cyborgwastaken/",
    essential: true,
  },
  {
    name: "LinkedIn",
    icon: "linkedin",
    link: "https://www.linkedin.com/company/ayuxcyb/",
    essential: true,
  },
  {
    name: "Instagram",
    icon: "instagram",
    link: "https://www.instagram.com/cyborgwastaken/",
    essential: true,
  },
  {
    name: "Threads",
    icon: "threads",
    link: "https://www.threads.com/@cyborgwastaken/",
    essential: false,
  },
  {
    name: "Email",
    icon: "email",
    link: `mailto:${person.email}`,
    essential: true,
  },
];

const home: Home = {
  path: "/",
  image: "/images/og/home.jpg",
  label: "Home",
  title: `${person.name}'s Portfolio`,
  description: `Portfolio website showcasing my work as a ${person.role}`,
  headline: <>Building bridges between design and code</>,
  featured: {
    display: true,
    title: (
      <Row gap="12" vertical="center">
        <strong className="ml-4">Resume</strong>{" "}
        <Line background="brand-alpha-strong" vert height="20" />
        <Text marginRight="4" onBackground="brand-medium">
          Download
        </Text>
      </Row>
    ),
    href: "/files/AyushmanDas.pdf",
  },
  subline: (
    <>
      I'm {person.firstName}, a {person.role.toLowerCase()} at{" "}
      <Text as="span" size="xl" weight="strong">Cyberpal.ai</Text>, where I build observability and reliability tooling <br /> for a live cybersecurity GRC product. After hours, I build my own projects.
    </>
  ),
};

const about: About = {
  path: "/about",   
  label: "About",
  title: `About – ${person.name}`,
  description: `Meet ${person.name}, ${person.role} from ${person.country} / ${person.city}`,
  tableOfContent: {
    display: true,
    subItems: false,
  },
  avatar: {
    display: true,
  },
  calendar: {
    display: true,
    link: "https://cal.com",
  },
  intro: {
    display: true,
    title: "Introduction",
    description: (
      <>
        {person.firstName} is a final-year B.Tech CS&E student (8.80 CGPA) and {person.city}-based {person.role.toLowerCase()} with
        backend, platform, and production deployment experience on a live cybersecurity GRC product, plus defence and research-lab
        internships. Proficient in Java, Python, Go and PostgreSQL, and skilled in reliability engineering (Prometheus, structured
        logging, distributed tracing, alerting), secure development, and networking fundamentals.
      </>
    ),
  },
  work: {
    display: true, // set to false to hide this section
    title: "Work Experience",
    experiences: [
      {
        company: "Technology Crest Corporation",
        timeframe: "02 2026 - Present",
        role: "Software Development Intern, Cyberpal.ai",
        achievements: [
          <>
            Built a server-management and observability console from scratch (Node.js, Express, Socket.IO) that supervises backend
            and frontend services, streaming live stdout/stderr to a web UI over WebSockets with cross-platform process-tree
            termination and graceful shutdown.
          </>,
          <>
            Instrumented the platform with Prometheus metrics and Pino structured logging, monitoring HTTP throughput, error rate
            and P99 latency on a custom dashboard; added edge-triggered alerts on heap usage, event-loop lag, error rate and latency
            plus health checks, replacing manual incident discovery with automated detection and faster recovery.
          </>,
          <>
            Implemented distributed tracing with correlation IDs, automatic secret redaction in logs, and a real-time pipeline that
            normalises and audits access/error logs and resolves user identity, supporting the product's GRC controls.
          </>,
        ],
        images: [
          // optional: leave the array empty if you don't want to display images
          // {
          //   src: "/images/projects/project-01/cover-01.jpg",
          //   alt: "Once UI Project",
          //   width: 16,
          //   height: 9,
          // },
        ],
      },
      {
        company: "DRDO - PXE, Defense Research & Development Organisation",
        timeframe: "05 - 06 2025",
        role: "Research & Development Intern, DRAD-MS & BLADE",
        achievements: [
          <>
            Designed, built and deployed two internal applications (DRAD-MS and the BLADEngine) for mission data management and
            trajectory analysis, inside a secure, access-controlled environment with strict handling and compliance requirements.
          </>,
          <>
            Automated manual infrastructure provisioning and deployment steps; diagnosed and eliminated recurring systemic errors
            in the trajectory-tracking pipeline, improving reliability of downstream analysis.
          </>,
        ],
        images: [],
      },
      {
        company: "Vellore Institute of Technology",
        timeframe: "05 - 06 2024",
        role: "Project Assistant, DST - SERB CRG Research Project",
        achievements: [
          <>
            Built a Python molecular-visualisation tool (PyMOL/OpenGL) interoperating with quantum chemistry packages (Gaussian,
            GAMESS, NW Chem, MOPAC); profiled and optimised the rendering path for large structures.
          </>,
        ],
        images: [],
      },
    ],
  },
  studies: {
    display: true, // set to false to hide this section
    title: "Studies",
    institutions: [
      {
        name: "Class X AISSE | Percentage : 90.8%",
        description: <>BJEM School - II, Bhubaneshwar | 2016 - 2021</>,
      },
      {
        name: "Class XII AISSCE | Percentage : 77.6%",
        description: <>ODM Public School, Bhubaneshwar | 2021 - 2023</>,
      },
      {
        name: "BTech Computer Science & Engineering | CGPA : 8.80",
        description: <>Vellore Institute of Technology, Bhopal | 2023 - 2027</>,
      },
      {
        name: "BS Data Science & Applications | Online",
        description: <>Indian Institute of Technology, Madras | 2024 - 2028</>,
      },
      
      
    ],
  },
  technical: {
    display: true, // set to false to hide this section
    title: "Technical skills",
    skills: [
      {
        title: "Languages",
        description: <></>,
        tags: [
          { name: "Java", icon: "java" },
          { name: "C#", icon: "csharp" },
          { name: "Python", icon: "python" },
          { name: "Go", icon: "go" },
          { name: "Rust", icon: "rust" },
          { name: "Swift", icon: "swift" },
          { name: "C++", icon: "cpp" },
        ],
        images: [],
      },
      {
        title: "Databases",
        description: <></>,
        tags: [
          { name: "PostgreSQL", icon: "postgresql" },
          { name: "Supabase", icon: "supabase" },
          { name: "SQLite", icon: "sqlite" },
          { name: "Redis", icon: "redis" },
        ],
        images: [],
      },
      {
        title: "Software & Web",
        description: <></>,
        tags: [
          { name: "React", icon: "react" },
          { name: "Node.js", icon: "nodejs" },
          { name: "Next.js", icon: "nextjs" },
          { name: "Express", icon: "express" },
          { name: "Socket.IO", icon: "socketio" },
          { name: "FastAPI", icon: "fastapi" },
          { name: "Git", icon: "git" },
          { name: "GitHub", icon: "github" },
        ],
        images: [],
      },
      {
        title: "Platform & Reliability",
        description: <></>,
        tags: [
          { name: "Prometheus", icon: "prometheus" },
          { name: "Docker", icon: "docker" },
          { name: "Kubernetes", icon: "kubernetes" },
          { name: "AWS", icon: "aws" },
          { name: "Google Cloud", icon: "googlecloud" },
        ],
        images: [],
      },
      {
        title: "Game Engine",
        description: <></>,
        tags: [
          { name: "Unity", icon: "unity" },
          { name: "Unreal Engine", icon: "unrealengine" },
        ],
        images: [],
      },
    ],
  },
};

const blog: Blog = {
  path: "/blog",
  label: "Blog",
  title: "Writing about design and tech...",
  description: `Read what ${person.name} has been up to recently`,
  // Create new blog posts by adding a new .mdx file to app/blog/posts
  // All posts will be listed on the /blog route
};

const work: Work = {
  path: "/work",
  label: "Work",
  title: `Projects – ${person.name}`,
  description: `Design and dev projects by ${person.name}`,
  // Create new project pages by adding a new .mdx file to app/blog/posts
  // All projects will be listed on the /home and /work routes
};

const gallery: Gallery = {
  path: "/gallery",
  label: "Gallery",
  title: `Photo gallery – ${person.name}`,
  description: `A photo collection by ${person.name}`,
  // Images by https://lorant.one
  // These are placeholder images, replace with your own
  images: [
    {
      src: "/images/gallery/horizontal-1.jpg",
      alt: "image",
      orientation: "horizontal",
    },
    {
      src: "/images/gallery/vertical-4.jpg",
      alt: "image",
      orientation: "vertical",
    },
    {
      src: "/images/gallery/horizontal-3.jpg",
      alt: "image",
      orientation: "horizontal",
    },
    {
      src: "/images/gallery/vertical-1.jpg",
      alt: "image",
      orientation: "vertical",
    },
    {
      src: "/images/gallery/vertical-2.jpg",
      alt: "image",
      orientation: "vertical",
    },
    {
      src: "/images/gallery/horizontal-2.jpg",
      alt: "image",
      orientation: "horizontal",
    },
    {
      src: "/images/gallery/horizontal-4.jpg",
      alt: "image",
      orientation: "horizontal",
    },
    {
      src: "/images/gallery/vertical-3.jpg",
      alt: "image",
      orientation: "vertical",
    },
  ],
};

export { person, social, newsletter, home, about, blog, work, gallery };
