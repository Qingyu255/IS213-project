import { InterestCategory } from "@/enums/InterestCategory";
import { Code, Trophy, Music, Palette, Plane, UtensilsCrossed, FlaskConical, Briefcase } from "lucide-react";

export const siteName = "Mulan";
  
export const interestCategoryArr: InterestCategory[] = [
    InterestCategory.Technology,
    InterestCategory.Sports,
    InterestCategory.Music,
    InterestCategory.Art,
    InterestCategory.Travel,
    InterestCategory.Food,
    InterestCategory.Science,
    InterestCategory.Business,
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
