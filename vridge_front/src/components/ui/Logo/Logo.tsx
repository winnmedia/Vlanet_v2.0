import Image from 'next/image';
import Link from 'next/link';

interface LogoProps {
  variant?: 'default' | 'white' | 'black';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

const sizeMap = {
  sm: { width: 100, height: 24, iconSize: 24 },
  md: { width: 140, height: 32, iconSize: 32 },
  lg: { width: 180, height: 40, iconSize: 40 },
  xl: { width: 200, height: 48, iconSize: 48 },
};

export function Logo({
  variant = 'default',
  size = 'md',
  showText = true,
  className = '',
}: LogoProps) {
  const { width, height, iconSize } = sizeMap[size];

  //    - vlanet-logo.svg 
  const logoMap = {
    default: '/images/logo/vlanet-logo.svg',
    white: '/images/logo/vlanet-logo.svg',
    black: '/images/logo/vlanet-logo.svg',
  };

  const iconMap = {
    default: '/images/logo/vlanet-logo.svg',
    white: '/images/logo/vlanet-logo.svg',
    black: '/images/logo/vlanet-logo.svg',
  };

  const logoSrc = showText ? logoMap[variant] : iconMap[variant];

  return (
    <Link href="/" className={`inline-flex items-center ${className}`}>
      <Image
        src={logoSrc}
        alt="VideoPlanet"
        width={showText ? width : iconSize}
        height={showText ? height : iconSize}
        priority
        className="h-auto"
      />
    </Link>
  );
}

export default Logo;