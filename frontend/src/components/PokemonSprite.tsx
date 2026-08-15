import type { Pokemon } from "../api/types";

const SIZES = { sm: "size-8", md: "size-12", lg: "size-20" } as const;

export function PokemonSprite({
  pokemon,
  size,
  className = "",
}: {
  pokemon: Pick<Pokemon, "sprite_url">;
  size: keyof typeof SIZES;
  className?: string;
}) {
  if (!pokemon.sprite_url) {
    if (size !== "lg") return null;
    return (
      <div
        className={`grid place-items-center text-xs text-slate-300 ${SIZES.lg} ${className}`}
      >
        no sprite
      </div>
    );
  }
  return (
    <img
      src={pokemon.sprite_url}
      alt=""
      loading="lazy"
      className={`${SIZES[size]} [image-rendering:pixelated] ${className}`}
    />
  );
}
