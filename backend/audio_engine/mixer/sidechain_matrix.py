"""
Sidechain Matrix
Manages intelligent sidechain compression between stems
"""

import numpy as np
from typing import Dict, List, Tuple
import logging

from .effects import StudioCompressor

logger = logging.getLogger(__name__)


class SidechainMatrix:
    """
    Manages sidechain compression relationships between stems
    """
    
    def __init__(self, sample_rate: int = 48000):
        """
        Initialize sidechain matrix
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        self.compressor = StudioCompressor(sample_rate)
        
        # Define sidechain relationships
        # Format: (source_role, target_role, settings)
        self.sidechain_rules = [
            # Kick ducks bass (classic)
            ('kick', 'bass', {
                'freq_range': (40, 120),
                'threshold_db': -20.0,
                'ratio': 10.0,
                'attack_ms': 5.0,
                'release_ms': 100.0,
                'description': 'Kick → Bass ducking'
            }),
            
            # Kick ducks synth bass
            ('kick', 'synth', {
                'freq_range': (40, 150),
                'threshold_db': -22.0,
                'ratio': 6.0,
                'attack_ms': 5.0,
                'release_ms': 120.0,
                'description': 'Kick → Synth bass ducking'
            }),
            
            # Lead vocal ducks music (broadband)
            ('vocal', 'synth', {
                'freq_range': None,  # Broadband
                'threshold_db': -25.0,
                'ratio': 3.0,
                'attack_ms': 10.0,
                'release_ms': 150.0,
                'description': 'Vocal → Music ducking'
            }),
            
            ('vocal', 'guitar', {
                'freq_range': None,
                'threshold_db': -25.0,
                'ratio': 3.0,
                'attack_ms': 10.0,
                'release_ms': 150.0,
                'description': 'Vocal → Guitar ducking'
            }),
            
            ('vocal', 'piano', {
                'freq_range': None,
                'threshold_db': -26.0,
                'ratio': 2.5,
                'attack_ms': 15.0,
                'release_ms': 180.0,
                'description': 'Vocal → Piano ducking'
            }),
            
            # Snare ducks vocal (presence region only)
            ('snare', 'vocal', {
                'freq_range': (2000, 5000),
                'threshold_db': -18.0,
                'ratio': 4.0,
                'attack_ms': 3.0,
                'release_ms': 60.0,
                'description': 'Snare → Vocal presence ducking'
            })
        ]
    
    def apply_sidechains(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str],
        masking_recommendations: List[Dict] = None
    ) -> Dict[str, np.ndarray]:
        """
        Apply all sidechain compression relationships
        
        Args:
            stems: Dictionary of {stem_name: audio}
            stem_roles: Dictionary of {stem_name: role}
            masking_recommendations: Optional recommendations from MaskingAnalyzer
            
        Returns:
            Dictionary of sidechain-processed stems
        """
        logger.info("Applying sidechain matrix...")
        
        processed_stems = stems.copy()
        sidechain_log = []
        
        # Apply rule-based sidechains
        for source_role, target_role, settings in self.sidechain_rules:
            # Find stems with these roles
            source_stems = [
                name for name, role in stem_roles.items()
                if role == source_role
            ]
            target_stems = [
                name for name, role in stem_roles.items()
                if role == target_role
            ]
            
            # Apply sidechain for each pair
            for source_name in source_stems:
                for target_name in target_stems:
                    if source_name in stems and target_name in processed_stems:
                        # Apply sidechain
                        processed_stems[target_name] = self.compressor.sidechain_compress(
                            audio=processed_stems[target_name],
                            sidechain=stems[source_name],
                            threshold_db=settings['threshold_db'],
                            ratio=settings['ratio'],
                            attack_ms=settings['attack_ms'],
                            release_ms=settings['release_ms'],
                            freq_range=settings['freq_range']
                        )
                        
                        sidechain_log.append(
                            f"{source_name} → {target_name}: {settings['description']}"
                        )
        
        # Apply masking-based sidechains if provided
        if masking_recommendations:
            for rec in masking_recommendations:
                if 'sidechain' in rec:
                    sc = rec['sidechain']
                    source = sc['source']
                    target = sc['target']
                    
                    if source in stems and target in processed_stems:
                        processed_stems[target] = self.compressor.sidechain_compress(
                            audio=processed_stems[target],
                            sidechain=stems[source],
                            threshold_db=-20.0,
                            ratio=sc.get('reduction_db', 3.0),
                            attack_ms=sc.get('attack_ms', 5.0),
                            release_ms=sc.get('release_ms', 100.0),
                            freq_range=sc.get('frequency_range')
                        )
                        
                        sidechain_log.append(
                            f"{source} → {target}: Masking-based"
                        )
        
        logger.info(f"Applied {len(sidechain_log)} sidechain relationships")
        for log in sidechain_log:
            logger.info(f"  - {log}")
        
        return processed_stems
    
    def analyze_sidechain_potential(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str]
    ) -> List[Dict]:
        """
        Analyze which sidechains would be beneficial
        
        Args:
            stems: Dictionary of stems
            stem_roles: Dictionary of stem roles
            
        Returns:
            List of recommended sidechain relationships
        """
        recommendations = []
        
        for source_role, target_role, settings in self.sidechain_rules:
            # Check if we have these roles
            has_source = any(role == source_role for role in stem_roles.values())
            has_target = any(role == target_role for role in stem_roles.values())
            
            if has_source and has_target:
                recommendations.append({
                    'source_role': source_role,
                    'target_role': target_role,
                    'settings': settings,
                    'benefit': self._estimate_benefit(source_role, target_role)
                })
        
        # Sort by benefit
        recommendations.sort(key=lambda x: x['benefit'], reverse=True)
        
        return recommendations
    
    def _estimate_benefit(
        self,
        source_role: str,
        target_role: str
    ) -> float:
        """
        Estimate benefit of sidechain (0-1)
        
        Args:
            source_role: Source stem role
            target_role: Target stem role
            
        Returns:
            Benefit score (0-1)
        """
        # High benefit pairs
        high_benefit = [
            ('kick', 'bass'),
            ('vocal', 'synth'),
            ('vocal', 'guitar')
        ]
        
        # Medium benefit pairs
        medium_benefit = [
            ('kick', 'synth'),
            ('snare', 'vocal'),
            ('vocal', 'piano')
        ]
        
        pair = (source_role, target_role)
        
        if pair in high_benefit:
            return 1.0
        elif pair in medium_benefit:
            return 0.6
        else:
            return 0.3
    
    def create_sidechain_report(
        self,
        stems: Dict[str, np.ndarray],
        stem_roles: Dict[str, str]
    ) -> Dict:
        """
        Create detailed sidechain analysis report
        
        Args:
            stems: Dictionary of stems
            stem_roles: Dictionary of stem roles
            
        Returns:
            Dictionary with sidechain analysis
        """
        recommendations = self.analyze_sidechain_potential(stems, stem_roles)
        
        report = {
            'total_potential_sidechains': len(recommendations),
            'high_benefit': [
                r for r in recommendations if r['benefit'] >= 0.8
            ],
            'medium_benefit': [
                r for r in recommendations if 0.4 <= r['benefit'] < 0.8
            ],
            'low_benefit': [
                r for r in recommendations if r['benefit'] < 0.4
            ],
            'recommendations': recommendations
        }
        
        return report
