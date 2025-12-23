    def _calculate_gain_reduction_simple(
        self,
        audio: np.ndarray,
        threshold: float,
        ceiling: float,
        release_ms: float
    ) -> np.ndarray:
        """Calculate gain reduction envelope (simple version without oversampling)"""
        
        # Calculate peak envelope (max of both channels)
        peak_envelope = np.max(np.abs(audio), axis=0)
        
        # Calculate required gain reduction
        gain_reduction = np.ones_like(peak_envelope)
        
        # Where signal exceeds threshold
        mask = peak_envelope > threshold
        
        # Calculate reduction to bring peaks to ceiling
        gain_reduction[mask] = ceiling / (peak_envelope[mask] + 1e-10)
        
        # Apply smooth release
        release_samples = int(release_ms * self.sample_rate / 1000)
        release_coef = np.exp(-1.0 / release_samples)
        
        # Smooth gain reduction (instant attack, smooth release)
        smoothed = np.zeros_like(gain_reduction)
        smoothed[0] = gain_reduction[0]
        
        for i in range(1, len(gain_reduction)):
            if gain_reduction[i] < smoothed[i-1]:
                # Attack (instant)
                smoothed[i] = gain_reduction[i]
            else:
                # Release (smooth)
                smoothed[i] = release_coef * smoothed[i-1] + (1 - release_coef) * gain_reduction[i]
        
        # Broadcast to stereo
        smoothed = np.tile(smoothed, (audio.shape[0], 1))
        
        return smoothed
