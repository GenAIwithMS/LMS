import React from 'react';

// The Lyceum's crest: a colonnade (the Lyceum was a school held in a covered walk)
// on a green shield. The same drawing as public/crest.svg.
const Crest: React.FC<{ size?: number; className?: string }> = ({ size = 32, className = '' }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" className={className} aria-hidden="true">
    <path d="M16 1.5 28.5 5.5V15c0 7.6-5.2 12.9-12.5 15.5C8.7 27.9 3.5 22.6 3.5 15V5.5Z" fill="#1f5b45" />
    <path d="M9 10.2 16 7.4l7 2.8Z" fill="#e9c98c" />
    <rect x="9" y="11.2" width="14" height="1.6" rx=".3" fill="#e9c98c" />
    <rect x="10.4" y="13.6" width="2.2" height="7.4" fill="#fbfaf6" />
    <rect x="14.9" y="13.6" width="2.2" height="7.4" fill="#fbfaf6" />
    <rect x="19.4" y="13.6" width="2.2" height="7.4" fill="#fbfaf6" />
    <rect x="8.6" y="21.8" width="14.8" height="1.8" rx=".3" fill="#e9c98c" />
  </svg>
);

export default Crest;
