import React from 'react';
import { connect } from 'get-starknet';
import { ETH_ADDRESS, STRK_ADDRESS, USDC_ADDRESS } from '../utils/constants';
import { ReactComponent as ETH } from 'assets/icons/ethereum.svg';
import { ReactComponent as USDC } from 'assets/icons/borrow_usdc.svg';
import { ReactComponent as STRK } from 'assets/icons/strk.svg';

const CRM_TOKEN_ADDRESS = "0x051c4b1fe3bf6774b87ad0b15ef5d1472759076e42944fff9b9f641ff13e5bbe";

// Check if the connected wallet holds the CRM token
export const checkForCRMToken = async (walletAddress) => {
  if (process.env.REACT_APP_IS_DEV === "true") {
    console.log("Development mode: Skipping CRM token check.");
    return true;
  }

  try {
    const starknet = await connect();
    if (!starknet.isConnected) {
      throw new Error('Wallet not connected');
    }

    const response = await starknet.provider.callContract({
      contractAddress: CRM_TOKEN_ADDRESS,
      entrypoint: 'balanceOf',
      calldata: [walletAddress],
    });

    const balance = BigInt(response.result[0]).toString();

    if (Number(balance) > 0) {
      return true;
    } else {
      alert("Beta testing is allowed only for users who hold the CRM token.");
      return false;
    }
  } catch (error) {
    console.error("Error checking CRM token balance:", error);
    throw error; // Ensures test will catch errors as thrown
  }
};

export const connectWallet = async () => {
  try {
    console.log('Attempting to connect to wallet...');

    const starknet = await connect({
      include: ['argentX', 'braavos'],
      modalMode: "alwaysAsk",
      modalTheme: "light",
    });

    if (!starknet) {
      console.error('No StarkNet object found');
      throw new Error('Failed to connect to wallet');
    }

    await starknet.enable();

    if (starknet.isConnected) {
      const address = starknet.selectedAddress;
      console.log('Wallet successfully connected. Address:', address);
      return address;
    } else {
      throw new Error('Wallet connection failed');
    }
  } catch (error) {
    console.error('Error connecting wallet:', error.message);
    throw error;
  }
};

export function logout() {
  localStorage.removeItem('wallet_id');
}

export async function getTokenBalances(walletAddress) {
  try {
    const starknet = await connect();
    if (!starknet.isConnected) {
      throw new Error('Wallet not connected');
    }

    const tokenBalances = {
      ETH: await getTokenBalance(starknet, walletAddress, ETH_ADDRESS),
      USDC: await getTokenBalance(starknet, walletAddress, USDC_ADDRESS),
      STRK: await getTokenBalance(starknet, walletAddress, STRK_ADDRESS),
    };

    return tokenBalances;
  } catch (error) {
    console.error('Error fetching token balances:', error);
    throw error;
  }
}

async function getTokenBalance(starknet, walletAddress, tokenAddress) {
  try {
    const response = await starknet.provider.callContract({
      contractAddress: tokenAddress,
      entrypoint: 'balanceOf',
      calldata: [walletAddress],
    });
    const tokenDecimals = (tokenAddress === USDC_ADDRESS) ? 6 : 18;
    const balance = BigInt(response.result[0]).toString();
    const readableBalance = (Number(balance) / (10 ** tokenDecimals)).toFixed(4);
    console.log(`Balance for token ${tokenAddress}:`, readableBalance);
    return readableBalance;
  } catch (error) {
    console.error(`Error fetching balance for token ${tokenAddress}:`, error);
    return '0';
  }
}


export const getBalances = async (walletId, setBalances) => {
  if (!walletId) return;
  try {
    const data = await getTokenBalances(walletId);

    const updatedBalances = [
      {
        icon: <ETH />,
        title: 'ETH',
        balance: data.ETH !== undefined ? data.ETH.toString() : '0.00',
      },
      {
        icon: <USDC />,
        title: 'USDC',
        balance: data.USDC !== undefined ? data.USDC.toString() : '0.00',
      },
      {
        icon: <STRK />,
        title: 'STRK',
        balance: data.STRK !== undefined ? data.STRK.toString() : '0.00',
      },
      // { icon: <DAI />, title: 'DAI', balance: data.DAI !== undefined ? data.DAI.toString() : '0.00' },  dont have DAI in the constants file
    ];

    setBalances(updatedBalances);
  } catch (error) {
    console.error('Error fetching user balances:', error);
  }
};

// Add this line for environments that don't recognize BigInt
const BigInt = window.BigInt;
