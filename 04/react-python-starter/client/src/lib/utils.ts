import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function to merge tailwind classes
 * 
 * @param inputs - Class values to merge
 * @returns Merged tailwind classes as a string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
