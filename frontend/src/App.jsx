import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import './globals.css';
import Header from './components/layout/header/Header';
import Dashboard from './pages/dashboard/Dashboard';
import Footer from './components/layout/footer/Footer';
import SpotnetApp from './pages/spotnet-app/SpotnetApp';
import Form from './pages/form/Form';
import { createPortal } from 'react-dom';
import { logout } from './services/wallet';
import { getTelegramUserWalletId } from './services/telegram';
import Documentation from './pages/documentation/Documentation';
import Withdraw from './pages/withdraw/Withdraw';
import { useWalletStore } from './stores/useWalletStore';
import { Notifier, notify } from './components/layout/notifier/Notifier';
import { useConnectWallet } from './hooks/useConnectWallet';
import OverviewPage from './pages/overview/Overview';
import { ActionModal } from './components/ui/action-modal';
import Stake from './pages/stake/Stake';
import { TELEGRAM_BOT_LINK } from './utils/constants';
import { useCheckMobile } from './hooks/useCheckMobile';
import PositionHistory from './pages/position-history/PositionHistory';
import WithdrawAll from 'pages/spotnet/dashboard/withdraw-all/WithdrawAll';

function App() {
  const { setWalletId, removeWalletId } = useWalletStore();
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();
  const [isMobileRestrictionModalOpen, setisMobileRestrictionModalOpen] = useState(true);
  const isMobile = useCheckMobile();
  
  const disableDesktopOnMobile = process.env.REACT_APP_DISABLE_DESKTOP_ON_MOBILE !== 'false';

  const connectWalletMutation = useConnectWallet(setWalletId);

  const handleConnectWallet = () => {
    connectWalletMutation.mutate();
  };

  const handleLogout = () => {
    logout();
    removeWalletId();
    closeModal();
    navigate('/');
  };

  const handleLogoutModal = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };


  const handleisMobileRestrictionModalClose = () => {
    setisMobileRestrictionModalOpen(false);
  };

  const openTelegramBot = () => {
    window.open(TELEGRAM_BOT_LINK, '_blank');
  };

  useEffect(() => {
    if (window.Telegram?.WebApp?.initData) {
      getTelegramUserWalletId(window.Telegram.WebApp.initDataUnsafe.user.id)
        .then((linked_wallet_id) => {
          setWalletId(linked_wallet_id);
          window.Telegram.WebApp.ready();
        })
        .catch((error) => {
          console.error('Error getting Telegram user wallet ID:', error);
          notify('Error loading wallet', "error");
          window.Telegram.WebApp.ready();
        });
    }
  }, [window.Telegram?.WebApp?.initDataUnsafe]);


  return (
    <div className="App">
      <Notifier />
      {showModal &&
        createPortal(
          <ActionModal
            isOpen={showModal}
            title="Logout"
            subTitle={'Do you want to disconnect your wallet and logout of this account?'}
            cancelLabel="Cancel"
            submitLabel="Yes, logout"
            submitAction={handleLogout}
            cancelAction={closeModal}
          />,
          document.body
        )}
      <Header onConnectWallet={handleConnectWallet} onLogout={handleLogoutModal} />
      <main>
        <Routes>
          <Route index element={<SpotnetApp onConnectWallet={handleConnectWallet} onLogout={handleLogout} />} />
          <Route path="/dashboard" element={<Dashboard telegramId={window?.Telegram?.WebApp?.initData?.user?.id} />} />
          <Route path="/withdraw" element={<Withdraw />} />
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/form" element={<Form />} />
          <Route path="/documentation" element={<Documentation />} />
          <Route path="/position-history" element={<PositionHistory />} />
          <Route path="/stake" element={<Stake />} />
          <Route path="/dashboard/withdraw-all" element={<WithdrawAll />} />
        </Routes>
      </main>
      <Footer />
      {isMobile && disableDesktopOnMobile && (
        <ActionModal
          isOpen={isMobileRestrictionModalOpen}
          title="Mobile website restriction"
          subTitle="Please, use desktop version or telegram mini-app"
          content={[]}
          cancelLabel="Cancel"
          submitLabel="Open in Telegram"
          submitAction={openTelegramBot}
          cancelAction={handleisMobileRestrictionModalClose}
        />
      )}
    </div>
  );
}

export default App;