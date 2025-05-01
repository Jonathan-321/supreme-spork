import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

const NavContainer = styled.nav`
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: ${props => props.theme.colors.background};
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  z-index: ${props => props.theme.zIndex.fixed};
`;

const NavItem = styled.button<{ isActive: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  outline: none;
  padding: 8px 12px;
  color: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.textLight};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.isActive ? props.theme.typography.fontWeight.semiBold : props.theme.typography.fontWeight.regular};
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.95);
  }
`;

const IconContainer = styled.div<{ isActive: boolean }>`
  font-size: 24px;
  margin-bottom: 4px;
  color: ${props => props.isActive ? props.theme.colors.primary : props.theme.colors.textLight};
`;

const Label = styled.span`
  font-size: 12px;
`;

// Simple icon components using emoji for the MVP
// In a real app, we would use SVG icons or an icon library
const HomeIcon = () => <span>🏠</span>;
const WeatherIcon = () => <span>🌦️</span>;
const FarmIcon = () => <span>🌱</span>;
const LoanIcon = () => <span>💰</span>;
const MarketIcon = () => <span>🛒</span>;

export const BottomNavigation: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const currentPath = location.pathname;

  const navItems = [
    { path: '/', label: t('dashboard'), icon: <HomeIcon /> },
    { path: '/weather', label: t('weather'), icon: <WeatherIcon /> },
    { path: '/farm', label: t('farm'), icon: <FarmIcon /> },
    { path: '/loans', label: t('loans'), icon: <LoanIcon /> },
    { path: '/market', label: t('market'), icon: <MarketIcon /> },
  ];

  return (
    <NavContainer>
      {navItems.map((item) => (
        <NavItem
          key={item.path}
          isActive={currentPath === item.path}
          onClick={() => navigate(item.path)}
          aria-label={item.label}
        >
          <IconContainer isActive={currentPath === item.path}>
            {item.icon}
          </IconContainer>
          <Label>{item.label}</Label>
        </NavItem>
      ))}
    </NavContainer>
  );
};

export default BottomNavigation;
