import { createContext, useState, useContext, ReactNode } from 'react';

// Define available domains for the site
const AVAILABLE_DOMAINS = [
  'https://animestars.org',
  'https://astars.club',
  'https://asstars1.astars.club',
  'https://as1.astars.club',
  'https://asstars.tv',
  'https://a1.astars.club',
  'https://insights.astars.club'
];

// Local storage key for saving the selected domain
const DOMAIN_STORAGE_KEY = 'anime_stars_domain';

interface DomainContextType {
  currentDomain: string;
  setCurrentDomain: (domain: string) => void;
  availableDomains: string[];
}

const DomainContext = createContext<DomainContextType | null>(null);

export const useDomain = () => {
  const context = useContext(DomainContext);
  if (!context) {
    throw new Error('useDomain must be used within a DomainProvider');
  }
  return context;
};

interface DomainProviderProps {
  children: ReactNode;
}

export const DomainProvider = ({ children }: DomainProviderProps) => {
  // Set default domain to the first in the list, but try to retrieve from localStorage first
  const [currentDomain, setCurrentDomainState] = useState<string>(() => {
    const savedDomain = localStorage.getItem(DOMAIN_STORAGE_KEY);
    return savedDomain || AVAILABLE_DOMAINS[0];
  });

  // Update domain and save to localStorage
  const setCurrentDomain = (domain: string) => {
    setCurrentDomainState(domain);
    localStorage.setItem(DOMAIN_STORAGE_KEY, domain);
  };

  const value = {
    currentDomain,
    setCurrentDomain,
    availableDomains: AVAILABLE_DOMAINS
  };

  return <DomainContext.Provider value={value}>{children}</DomainContext.Provider>;
}; 