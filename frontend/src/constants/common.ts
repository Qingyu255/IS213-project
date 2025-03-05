import { Code, Trophy, Music, Palette, Plane, UtensilsCrossed, FlaskConical, Briefcase } from "lucide-react";

export const siteName = "Mulan";

export const interestCategories = [
    "Technology",
    "Sports",
    "Music",
    "Art",
    "Travel",
    "Food",
    "Science",
    "Business",
];

export const interestCategoryIcons: Record<string, React.FC<React.SVGProps<SVGSVGElement>>> = {
    Technology: Code,
    Sports: Trophy,
    Music: Music,
    Art: Palette,
    Travel: Plane,
    Food: UtensilsCrossed,
    Science: FlaskConical,
    Business: Briefcase,
  };