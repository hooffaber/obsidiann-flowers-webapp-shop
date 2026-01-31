import { Smartphone } from 'lucide-react';

export default function OopsPage() {
  const telegramBotUrl = `https://t.me/${import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'your_bot'}`;
  const telegramChannel = import.meta.env.VITE_TELEGRAM_CHANNEL_URL || '';
  const instagramUrl = import.meta.env.VITE_INSTAGRAM_URL || '';

  // QR code generated from bot URL
  const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(telegramBotUrl)}`;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-sm w-full text-center space-y-8">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Smartphone className="w-8 h-8 text-primary" />
          </div>
        </div>

        {/* Title */}
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold text-foreground">
            Только через Telegram
          </h1>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Наш магазин работает как Telegram Mini App.
            Отсканируйте QR-код или перейдите по ссылке ниже.
          </p>
        </div>

        {/* QR Code */}
        <div className="flex justify-center">
          <div className="p-4 bg-white rounded-2xl shadow-sm">
            <img
              src={qrCodeUrl}
              alt="QR код для Telegram бота"
              className="w-48 h-48"
            />
          </div>
        </div>

        {/* Links */}
        <div className="space-y-3">
          <a
            href={telegramBotUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 w-full py-3 px-4 bg-[#2AABEE] hover:bg-[#229ED9] text-white font-medium rounded-xl transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
            Открыть в Telegram
          </a>

          {(telegramChannel || instagramUrl) && (
            <div className="flex gap-3">
              {telegramChannel && (
                <a
                  href={telegramChannel}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3 px-4 bg-muted hover:bg-muted/80 text-foreground font-medium rounded-xl transition-colors text-sm"
                >
                  Telegram канал
                </a>
              )}
              {instagramUrl && (
                <a
                  href={instagramUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3 px-4 bg-muted hover:bg-muted/80 text-foreground font-medium rounded-xl transition-colors text-sm"
                >
                  Instagram
                </a>
              )}
            </div>
          )}
        </div>

        {/* Footer note */}
        <p className="text-xs text-muted-foreground/60">
          Telegram Mini App обеспечивает безопасную авторизацию и удобную оплату
        </p>
      </div>
    </div>
  );
}
