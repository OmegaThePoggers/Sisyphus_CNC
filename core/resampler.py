import numpy as np

class PathResampler:
    @staticmethod
    def resample_path(points, num_points):
        """Resample a single continuous polyline into `num_points` evenly spaced points."""
        points = np.asarray(points)
        if len(points) == 0:
            return points
            
        # Compute cumulative distance along the path
        diffs = np.diff(points, axis=0)
        dists = np.linalg.norm(diffs, axis=1)
        cum_dists = np.concatenate(([0.0], np.cumsum(dists)))
        
        total_dist = cum_dists[-1]
        
        if total_dist == 0 or num_points == 1:
            return np.tile(points[0], (num_points, 1))

        # Evenly spaced targets
        target_dists = np.linspace(0, total_dist, num_points)
        
        # Interpolate x and y independently against cumulative distance
        resampled_x = np.interp(target_dists, cum_dists, points[:, 0])
        resampled_y = np.interp(target_dists, cum_dists, points[:, 1])
        
        return np.column_stack((resampled_x, resampled_y))

    @staticmethod
    def interpolate_paths(path_a, path_b, alpha):
        """
        Interpolates between two paths (assumed to have the same number of points).
        alpha = 0 returns path_a, alpha = 1 returns path_b.
        """
        return (1.0 - alpha) * path_a + alpha * path_b
