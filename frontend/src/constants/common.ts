import { InterestCategory } from "@/enums/InterestCategory";
import { Code, Trophy, Music, Palette, Plane, UtensilsCrossed, FlaskConical, Briefcase } from "lucide-react";

export const siteName = "Mulan";
  
export const InterestCategoryArr: InterestCategory[] = [
    InterestCategory.Technology,
    InterestCategory.Sports,
    InterestCategory.Music,
    InterestCategory.Art,
    InterestCategory.Travel,
    InterestCategory.Food,
    InterestCategory.Science,
    InterestCategory.Business,
];

export const InterestCategoryIcons: Record<string, React.FC<React.SVGProps<SVGSVGElement>>> = {
    technology: Code,
    sports: Trophy,
    music: Music,
    art: Palette,
    travel: Plane,
    food: UtensilsCrossed,
    science: FlaskConical,
    business: Briefcase,
};
