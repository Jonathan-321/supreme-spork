import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import language resources
const resources = {
  en: {
    translation: {
      // General
      app_name: 'AgriFinance',
      loading: 'Loading...',
      offline_message: 'You are currently offline',
      online_message: 'Back online',
      update_available: 'Update available',
      update_now: 'Update Now',
      
      // Authentication
      login: 'Login',
      register: 'Register',
      logout: 'Logout',
      email: 'Email',
      phone: 'Phone Number',
      password: 'Password',
      confirm_password: 'Confirm Password',
      forgot_password: 'Forgot Password?',
      create_account: 'Create Account',
      already_have_account: 'Already have an account?',
      
      // Dashboard
      dashboard: 'Dashboard',
      welcome: 'Welcome',
      credit_score: 'Credit Score',
      weather_forecast: 'Weather Forecast',
      active_loans: 'Active Loans',
      farm_summary: 'Farm Summary',
      climate_risk: 'Climate Risk',
      
      // Weather
      weather: 'Weather',
      today: 'Today',
      tomorrow: 'Tomorrow',
      weekly_forecast: 'Weekly Forecast',
      temperature: 'Temperature',
      humidity: 'Humidity',
      rainfall: 'Rainfall',
      wind: 'Wind',
      
      // Farm
      farm: 'Farm',
      my_farms: 'My Farms',
      add_farm: 'Add Farm',
      crop_health: 'Crop Health',
      soil_moisture: 'Soil Moisture',
      pest_risk: 'Pest Risk',
      harvest_estimate: 'Harvest Estimate',
      
      // Loans
      loans: 'Loans',
      my_loans: 'My Loans',
      apply_for_loan: 'Apply for Loan',
      loan_amount: 'Loan Amount',
      interest_rate: 'Interest Rate',
      duration: 'Duration',
      repayment_schedule: 'Repayment Schedule',
      next_payment: 'Next Payment',
      payment_history: 'Payment History',
      
      // Credit
      credit: 'Credit',
      credit_history: 'Credit History',
      improve_score: 'Improve Score',
      score_factors: 'Score Factors',
      
      // Market
      market: 'Market',
      market_prices: 'Market Prices',
      price_trends: 'Price Trends',
      sell_crops: 'Sell Crops',
      
      // Profile
      profile: 'Profile',
      personal_info: 'Personal Information',
      settings: 'Settings',
      language: 'Language',
      notifications: 'Notifications',
      help: 'Help & Support',
      about: 'About',
      
      // Offline
      offline_title: 'You\'re Offline',
      offline_message_long: 'No internet connection. Some features may be limited.',
      available_offline: 'Available Offline',
      
      // Errors
      error_generic: 'Something went wrong',
      error_login: 'Login failed. Please check your credentials.',
      error_register: 'Registration failed. Please try again.',
      error_connection: 'Connection error. Please check your internet.',
      
      // Actions
      save: 'Save',
      cancel: 'Cancel',
      confirm: 'Confirm',
      apply: 'Apply',
      submit: 'Submit',
      next: 'Next',
      previous: 'Previous',
      search: 'Search',
      filter: 'Filter',
      sort: 'Sort',
      refresh: 'Refresh',
    }
  },
  fr: {
    translation: {
      // General
      app_name: 'AgriFinance',
      loading: 'Chargement...',
      offline_message: 'Vous êtes actuellement hors ligne',
      online_message: 'De retour en ligne',
      update_available: 'Mise à jour disponible',
      update_now: 'Mettre à jour',
      
      // Authentication
      login: 'Connexion',
      register: 'S\'inscrire',
      logout: 'Déconnexion',
      email: 'Email',
      phone: 'Numéro de téléphone',
      password: 'Mot de passe',
      confirm_password: 'Confirmer le mot de passe',
      forgot_password: 'Mot de passe oublié?',
      create_account: 'Créer un compte',
      already_have_account: 'Vous avez déjà un compte?',
      
      // Dashboard
      dashboard: 'Tableau de bord',
      welcome: 'Bienvenue',
      credit_score: 'Score de crédit',
      weather_forecast: 'Prévisions météo',
      active_loans: 'Prêts actifs',
      farm_summary: 'Résumé de la ferme',
      climate_risk: 'Risque climatique',
      
      // Weather
      weather: 'Météo',
      today: 'Aujourd\'hui',
      tomorrow: 'Demain',
      weekly_forecast: 'Prévisions hebdomadaires',
      temperature: 'Température',
      humidity: 'Humidité',
      rainfall: 'Précipitations',
      wind: 'Vent',
      
      // Farm
      farm: 'Ferme',
      my_farms: 'Mes fermes',
      add_farm: 'Ajouter une ferme',
      crop_health: 'Santé des cultures',
      soil_moisture: 'Humidité du sol',
      pest_risk: 'Risque de parasites',
      harvest_estimate: 'Estimation de la récolte',
      
      // Loans
      loans: 'Prêts',
      my_loans: 'Mes prêts',
      apply_for_loan: 'Demander un prêt',
      loan_amount: 'Montant du prêt',
      interest_rate: 'Taux d\'intérêt',
      duration: 'Durée',
      repayment_schedule: 'Calendrier de remboursement',
      next_payment: 'Prochain paiement',
      payment_history: 'Historique des paiements',
      
      // Credit
      credit: 'Crédit',
      credit_history: 'Historique de crédit',
      improve_score: 'Améliorer le score',
      score_factors: 'Facteurs de score',
      
      // Market
      market: 'Marché',
      market_prices: 'Prix du marché',
      price_trends: 'Tendances des prix',
      sell_crops: 'Vendre des cultures',
      
      // Profile
      profile: 'Profil',
      personal_info: 'Informations personnelles',
      settings: 'Paramètres',
      language: 'Langue',
      notifications: 'Notifications',
      help: 'Aide et support',
      about: 'À propos',
      
      // Offline
      offline_title: 'Vous êtes hors ligne',
      offline_message_long: 'Pas de connexion internet. Certaines fonctionnalités peuvent être limitées.',
      available_offline: 'Disponible hors ligne',
      
      // Errors
      error_generic: 'Une erreur s\'est produite',
      error_login: 'Échec de la connexion. Veuillez vérifier vos identifiants.',
      error_register: 'Échec de l\'inscription. Veuillez réessayer.',
      error_connection: 'Erreur de connexion. Veuillez vérifier votre internet.',
      
      // Actions
      save: 'Enregistrer',
      cancel: 'Annuler',
      confirm: 'Confirmer',
      apply: 'Appliquer',
      submit: 'Soumettre',
      next: 'Suivant',
      previous: 'Précédent',
      search: 'Rechercher',
      filter: 'Filtrer',
      sort: 'Trier',
      refresh: 'Actualiser',
    }
  },
  sw: {
    translation: {
      // General
      app_name: 'AgriFinance',
      loading: 'Inapakia...',
      offline_message: 'Huna mtandao kwa sasa',
      online_message: 'Mtandao umerudi',
      update_available: 'Maboresho yapo',
      update_now: 'Sasisha Sasa',
      
      // Authentication
      login: 'Ingia',
      register: 'Jisajili',
      logout: 'Toka',
      email: 'Barua pepe',
      phone: 'Namba ya simu',
      password: 'Neno la siri',
      confirm_password: 'Thibitisha neno la siri',
      forgot_password: 'Umesahau neno la siri?',
      create_account: 'Fungua akaunti',
      already_have_account: 'Una akaunti tayari?',
      
      // Dashboard
      dashboard: 'Dashibodi',
      welcome: 'Karibu',
      credit_score: 'Alama ya mkopo',
      weather_forecast: 'Utabiri wa hali ya hewa',
      active_loans: 'Mikopo hai',
      farm_summary: 'Muhtasari wa shamba',
      climate_risk: 'Hatari ya hali ya hewa',
      
      // Weather
      weather: 'Hali ya hewa',
      today: 'Leo',
      tomorrow: 'Kesho',
      weekly_forecast: 'Utabiri wa wiki',
      temperature: 'Joto',
      humidity: 'Unyevu',
      rainfall: 'Mvua',
      wind: 'Upepo',
      
      // Farm
      farm: 'Shamba',
      my_farms: 'Mashamba yangu',
      add_farm: 'Ongeza shamba',
      crop_health: 'Afya ya mazao',
      soil_moisture: 'Unyevu wa udongo',
      pest_risk: 'Hatari ya wadudu',
      harvest_estimate: 'Makadirio ya mavuno',
      
      // Loans
      loans: 'Mikopo',
      my_loans: 'Mikopo yangu',
      apply_for_loan: 'Omba mkopo',
      loan_amount: 'Kiasi cha mkopo',
      interest_rate: 'Kiwango cha riba',
      duration: 'Muda',
      repayment_schedule: 'Ratiba ya malipo',
      next_payment: 'Malipo yajayo',
      payment_history: 'Historia ya malipo',
      
      // Credit
      credit: 'Mkopo',
      credit_history: 'Historia ya mkopo',
      improve_score: 'Boresha alama',
      score_factors: 'Vigezo vya alama',
      
      // Market
      market: 'Soko',
      market_prices: 'Bei za soko',
      price_trends: 'Mwenendo wa bei',
      sell_crops: 'Uza mazao',
      
      // Profile
      profile: 'Wasifu',
      personal_info: 'Taarifa binafsi',
      settings: 'Mipangilio',
      language: 'Lugha',
      notifications: 'Arifa',
      help: 'Msaada',
      about: 'Kuhusu',
      
      // Offline
      offline_title: 'Huna mtandao',
      offline_message_long: 'Hakuna muunganisho wa mtandao. Baadhi ya huduma zinaweza kuwa na vikwazo.',
      available_offline: 'Inapatikana bila mtandao',
      
      // Errors
      error_generic: 'Kuna hitilafu imetokea',
      error_login: 'Imeshindwa kuingia. Tafadhali angalia taarifa zako.',
      error_register: 'Usajili umeshindwa. Tafadhali jaribu tena.',
      error_connection: 'Hitilafu ya muunganisho. Tafadhali angalia mtandao wako.',
      
      // Actions
      save: 'Hifadhi',
      cancel: 'Ghairi',
      confirm: 'Thibitisha',
      apply: 'Omba',
      submit: 'Wasilisha',
      next: 'Endelea',
      previous: 'Rudi',
      search: 'Tafuta',
      filter: 'Chuja',
      sort: 'Panga',
      refresh: 'Onyesha upya',
    }
  }
};

// Initialize i18next
i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // Default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already safes from XSS
    },
    react: {
      useSuspense: false,
    },
  });

export default i18n;
