import { cn } from '@/lib/utils';
import { Category } from '@/types/shop';

interface CategoryChipsProps {
  categories: Category[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
}

export function CategoryChips({ categories, selectedId, onSelect }: CategoryChipsProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4">
      <button
        onClick={() => onSelect(null)}
        className={cn(
          "flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
          selectedId === null
            ? "bg-primary text-primary-foreground shadow-button"
            : "bg-muted text-muted-foreground hover:bg-muted/80"
        )}
      >
        Все
      </button>
      {categories.filter(c => c.is_active).map((category) => (
        <button
          key={category.id}
          onClick={() => onSelect(category.id)}
          className={cn(
            "flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
            selectedId === category.id
              ? "bg-primary text-primary-foreground shadow-button"
              : "bg-muted text-muted-foreground hover:bg-muted/80"
          )}
        >
          {category.title}
        </button>
      ))}
    </div>
  );
}
