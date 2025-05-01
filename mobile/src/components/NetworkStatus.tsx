import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

interface NetworkStatusProps {
  isOnline: boolean;
}

const StatusBar = styled.div<{ isOnline: boolean; isVisible: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: ${props => props.isOnline ? props.theme.colors.success : props.theme.colors.error};
  color: ${props => props.theme.colors.textInverted};
  padding: 8px 16px;
  font-size: 14px;
  text-align: center;
  z-index: ${props => props.theme.zIndex.toast};
  transform: translateY(${props => props.isVisible ? '0' : '-100%'});
  transition: transform 0.3s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StatusIcon = styled.span`
  margin-right: 8px;
  font-size: 16px;
`;

export const NetworkStatus: React.FC<NetworkStatusProps> = ({ isOnline }) => {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [lastStatus, setLastStatus] = useState(isOnline);

  useEffect(() => {
    // Only show the status bar when the status changes
    if (lastStatus !== isOnline) {
      setIsVisible(true);
      setLastStatus(isOnline);
      
      // Hide the status bar after 3 seconds
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [isOnline, lastStatus]);

  return (
    <StatusBar isOnline={isOnline} isVisible={isVisible}>
      <StatusIcon>
        {isOnline ? '✓' : '✗'}
      </StatusIcon>
      {isOnline ? t('online_message') : t('offline_message')}
    </StatusBar>
  );
};

export default NetworkStatus;
