import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
  if (!dateString) return 'No date';
  
  try {
    // Handle Django datetime format (ISO string)
    let date: Date;
    
    if (dateString.includes('T') || dateString.includes('Z')) {
      // ISO format - parse directly
      date = new Date(dateString);
    } else {
      // Try parsing as Django format (YYYY-MM-DD HH:MM:SS)
      date = new Date(dateString.replace(' ', 'T'));
    }
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return 'Invalid date';
    }
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch (error) {
    console.error('Error formatting date:', error, 'Date string:', dateString);
    return 'Invalid date';
  }
}
