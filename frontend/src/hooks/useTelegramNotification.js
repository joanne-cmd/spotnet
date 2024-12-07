import { useMutation } from "@tanstack/react-query";
import { subscribeToNotification, generateTelegramLink } from "services/telegram";
import { notifyError, notifySuccess } from "utils/notification";

const useTelegramNotification = () => {
    const mutation = useMutation({
        mutationFn: async ({ telegramId, walletId }) => {
            if (!telegramId) {
                // Get subscription link from backend
                const { subscription_link } = await generateTelegramLink(walletId);
                window.open(subscription_link, '_blank');
                return;
            }
            return await subscribeToNotification(telegramId, walletId);
        },
        onSuccess: () => {
            notifySuccess("Subscribed to notifications successfully!");
        },
        onError: (error) => {
            notifyError(error?.message || "Failed to subscribe. Please try again.");
        },
    });

    return {
        subscribe: mutation.mutate,
        isLoading: mutation.isPending,
    };
};

export default useTelegramNotification;
