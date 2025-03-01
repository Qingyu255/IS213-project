# Frontend

## Prerequisites

- Node.js (v20 or later)
- pnpm (v8 or later)
- Docker and Docker Compose (if running with other services)

## Development Setup

1. Install dependencies:

```bash
pnpm install
```

2. Run the development server:

```bash
pnpm dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

## Running with Docker

### Development Mode

```bash
# From the root directory of the project
docker-compose up frontend
```

### Production Build

```bash
# Build the frontend image
docker build -t frontend-client ./frontend/client

# Run the container
docker run -p 3000:3000 frontend-client
```

## Project Structure

```
frontend/client/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── page.tsx      # Main page component
│   │   └── layout.tsx    # Root layout
│   └── components/       # Shared components
├── public/              # Static files
├── tailwind.config.ts   # Tailwind CSS configuration
├── next.config.ts       # Next.js configuration
└── package.json         # Project dependencies
```

## Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint
- `pnpm format` - Format code with Prettier
