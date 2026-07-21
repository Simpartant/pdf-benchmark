// Application route constants

export const ROUTES = {
  HOME: "/",
  UPLOAD: "/upload",
  PROCESSING: "/processing",
  RESULTS: "/results",
  COMPARISON: "/comparison",
  COMPARE: "/compare",
  HISTORY: "/history",
  BENCHMARK: "/benchmark",
} as const;

export type Route = (typeof ROUTES)[keyof typeof ROUTES];

/**
 * Build route with query parameters
 * @param route - Base route
 * @param params - Query parameters
 * @returns Full route with query string
 */
export function buildRoute(
  route: Route,
  params?: Record<string, string | number>,
): string {
  if (!params) return route;

  const queryString = Object.entries(params)
    .map(
      ([key, value]) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(value)}`,
    )
    .join("&");

  return `${route}?${queryString}`;
}
