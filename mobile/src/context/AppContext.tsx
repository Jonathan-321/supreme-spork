import React, { createContext, useContext, useState, useEffect } from 'react';
import localforage from 'localforage';

// Define types for our context
type FarmerType = 'SMALLHOLDER' | 'MEDIUM' | 'LARGE' | 'COOPERATIVE';

interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  farmerType: FarmerType;
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  profileComplete: boolean;
}

interface Farm {
  id: string;
  name: string;
  size: number;
  cropTypes: string[];
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  soilType: string;
  lastHarvest?: Date;
  cropHealth: number; // 0-100%
}

interface Loan {
  id: string;
  amount: number;
  interestRate: number;
  startDate: Date;
  endDate: Date;
  status: 'PENDING' | 'APPROVED' | 'ACTIVE' | 'COMPLETED' | 'DEFAULTED';
  nextPaymentDate?: Date;
  nextPaymentAmount?: number;
}

interface Weather {
  current: {
    temperature: number;
    humidity: number;
    windSpeed: number;
    condition: string;
    icon: string;
  };
  forecast: Array<{
    date: Date;
    maxTemp: number;
    minTemp: number;
    condition: string;
    icon: string;
    precipitation: number;
  }>;
  lastUpdated: Date;
}

interface MarketPrice {
  cropType: string;
  currentPrice: number;
  unit: string;
  trend: 'UP' | 'DOWN' | 'STABLE';
  priceHistory: Array<{
    date: Date;
    price: number;
  }>;
  lastUpdated: Date;
}

interface CreditScore {
  score: number; // 0-1000
  category: 'VERY_POOR' | 'POOR' | 'FAIR' | 'GOOD' | 'EXCELLENT';
  factors: string[];
  history: Array<{
    date: Date;
    score: number;
  }>;
  lastUpdated: Date;
}

interface AppContextType {
  user: User | null;
  farms: Farm[];
  loans: Loan[];
  weather: Weather | null;
  marketPrices: MarketPrice[];
  creditScore: CreditScore | null;
  isLoading: boolean;
  error: string | null;
  isOfflineMode: boolean;
  pendingSyncOperations: any[];
  setUser: (user: User | null) => void;
  setFarms: (farms: Farm[]) => void;
  setLoans: (loans: Loan[]) => void;
  setWeather: (weather: Weather | null) => void;
  setMarketPrices: (prices: MarketPrice[]) => void;
  setCreditScore: (score: CreditScore | null) => void;
  addPendingSyncOperation: (operation: any) => void;
  clearPendingSyncOperations: () => void;
  syncData: () => Promise<void>;
}

// Create context with default values
const AppContext = createContext<AppContextType>({
  user: null,
  farms: [],
  loans: [],
  weather: null,
  marketPrices: [],
  creditScore: null,
  isLoading: false,
  error: null,
  isOfflineMode: false,
  pendingSyncOperations: [],
  setUser: () => {},
  setFarms: () => {},
  setLoans: () => {},
  setWeather: () => {},
  setMarketPrices: () => {},
  setCreditScore: () => {},
  addPendingSyncOperation: () => {},
  clearPendingSyncOperations: () => {},
  syncData: async () => {},
});

// Initialize localforage instances for different data types
const userStore = localforage.createInstance({ name: 'user' });
const farmsStore = localforage.createInstance({ name: 'farms' });
const loansStore = localforage.createInstance({ name: 'loans' });
const weatherStore = localforage.createInstance({ name: 'weather' });
const marketStore = localforage.createInstance({ name: 'market' });
const creditStore = localforage.createInstance({ name: 'credit' });
const syncStore = localforage.createInstance({ name: 'sync' });

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [weather, setWeather] = useState<Weather | null>(null);
  const [marketPrices, setMarketPrices] = useState<MarketPrice[]>([]);
  const [creditScore, setCreditScore] = useState<CreditScore | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isOfflineMode, setIsOfflineMode] = useState<boolean>(!navigator.onLine);
  const [pendingSyncOperations, setPendingSyncOperations] = useState<any[]>([]);

  // Load data from local storage on initial load
  useEffect(() => {
    const loadLocalData = async () => {
      try {
        setIsLoading(true);
        
        // Load user data
        const userData = await userStore.getItem<User>('currentUser');
        if (userData) setUser(userData);
        
        // Load farms data
        const farmsData = await farmsStore.getItem<Farm[]>('farms');
        if (farmsData) setFarms(farmsData);
        
        // Load loans data
        const loansData = await loansStore.getItem<Loan[]>('loans');
        if (loansData) setLoans(loansData);
        
        // Load weather data
        const weatherData = await weatherStore.getItem<Weather>('weather');
        if (weatherData) setWeather(weatherData);
        
        // Load market prices data
        const marketData = await marketStore.getItem<MarketPrice[]>('prices');
        if (marketData) setMarketPrices(marketData);
        
        // Load credit score data
        const creditData = await creditStore.getItem<CreditScore>('score');
        if (creditData) setCreditScore(creditData);
        
        // Load pending sync operations
        const syncData = await syncStore.getItem<any[]>('pendingOperations');
        if (syncData) setPendingSyncOperations(syncData);
        
      } catch (err) {
        setError('Failed to load local data');
        console.error('Error loading local data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadLocalData();
    
    // Set up online/offline event listeners
    const handleOnline = () => setIsOfflineMode(false);
    const handleOffline = () => setIsOfflineMode(true);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Save data to local storage whenever it changes
  useEffect(() => {
    if (user) userStore.setItem('currentUser', user);
  }, [user]);
  
  useEffect(() => {
    if (farms.length > 0) farmsStore.setItem('farms', farms);
  }, [farms]);
  
  useEffect(() => {
    if (loans.length > 0) loansStore.setItem('loans', loans);
  }, [loans]);
  
  useEffect(() => {
    if (weather) weatherStore.setItem('weather', weather);
  }, [weather]);
  
  useEffect(() => {
    if (marketPrices.length > 0) marketStore.setItem('prices', marketPrices);
  }, [marketPrices]);
  
  useEffect(() => {
    if (creditScore) creditStore.setItem('score', creditScore);
  }, [creditScore]);
  
  useEffect(() => {
    if (pendingSyncOperations.length > 0) {
      syncStore.setItem('pendingOperations', pendingSyncOperations);
    }
  }, [pendingSyncOperations]);

  // Add a new operation to the pending sync queue
  const addPendingSyncOperation = (operation: any) => {
    setPendingSyncOperations(prev => [...prev, { ...operation, timestamp: new Date() }]);
  };

  // Clear all pending sync operations
  const clearPendingSyncOperations = () => {
    setPendingSyncOperations([]);
    syncStore.removeItem('pendingOperations');
  };

  // Sync data with the server when online
  const syncData = async () => {
    if (isOfflineMode || pendingSyncOperations.length === 0) {
      return;
    }

    try {
      setIsLoading(true);
      
      // In a real app, we would send the pending operations to the server
      // For now, we'll simulate a successful sync
      console.log('Syncing data with server:', pendingSyncOperations);
      
      // Wait for a short time to simulate network request
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Clear pending operations after successful sync
      clearPendingSyncOperations();
      
      // Fetch latest data from server (simulated)
      // In a real app, we would make API calls here
      console.log('Fetching latest data from server');
      
      setError(null);
    } catch (err) {
      setError('Failed to sync data with server');
      console.error('Error syncing data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Attempt to sync data whenever we go online
  useEffect(() => {
    if (!isOfflineMode && pendingSyncOperations.length > 0) {
      syncData();
    }
  }, [isOfflineMode]);

  const contextValue: AppContextType = {
    user,
    farms,
    loans,
    weather,
    marketPrices,
    creditScore,
    isLoading,
    error,
    isOfflineMode,
    pendingSyncOperations,
    setUser,
    setFarms,
    setLoans,
    setWeather,
    setMarketPrices,
    setCreditScore,
    addPendingSyncOperation,
    clearPendingSyncOperations,
    syncData,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the AppContext
export const useAppContext = () => useContext(AppContext);

export default AppContext;
