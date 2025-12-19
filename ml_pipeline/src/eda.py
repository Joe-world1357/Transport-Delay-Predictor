"""
Exploratory Data Analysis Module (FR-14 to FR-16)
Visualizes delay distributions and relationships
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class EDA:
    """Performs exploratory data analysis per SRS requirements"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "outputs/visualizations"):
        """
        Initialize EDA
        
        Args:
            df: DataFrame to analyze
            output_dir: Directory to save visualizations
        """
        self.df = df.copy()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def visualize_delay_distribution(self) -> str:
        """
        Visualize delay distributions (FR-14)
        
        Returns:
            Path to saved visualization
        """
        logger.info("Visualizing delay distribution...")
        
        if 'delay_minutes' not in self.df.columns:
            logger.warning("delay_minutes column not found")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Delay Distribution Analysis', fontsize=16, fontweight='bold')
        
        # Histogram
        axes[0, 0].hist(self.df['delay_minutes'], bins=30, edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Delay Distribution (Histogram)')
        axes[0, 0].set_xlabel('Delay (minutes)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].axvline(self.df['delay_minutes'].mean(), color='red', 
                          linestyle='--', label=f'Mean: {self.df["delay_minutes"].mean():.2f}')
        axes[0, 0].legend()
        
        # Box plot
        axes[0, 1].boxplot(self.df['delay_minutes'], vert=True)
        axes[0, 1].set_title('Delay Distribution (Box Plot)')
        axes[0, 1].set_ylabel('Delay (minutes)')
        
        # Density plot
        axes[1, 0].hist(self.df['delay_minutes'], bins=30, density=True, 
                       alpha=0.7, edgecolor='black')
        self.df['delay_minutes'].plot(kind='density', ax=axes[1, 0], color='red')
        axes[1, 0].set_title('Delay Distribution (Density)')
        axes[1, 0].set_xlabel('Delay (minutes)')
        axes[1, 0].set_ylabel('Density')
        
        # Statistics summary
        stats_text = f"""
        Statistics Summary:
        Mean: {self.df['delay_minutes'].mean():.2f} min
        Median: {self.df['delay_minutes'].median():.2f} min
        Std: {self.df['delay_minutes'].std():.2f} min
        Min: {self.df['delay_minutes'].min():.2f} min
        Max: {self.df['delay_minutes'].max():.2f} min
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, 
                        verticalalignment='center', family='monospace')
        axes[1, 1].axis('off')
        axes[1, 1].set_title('Delay Statistics')
        
        plt.tight_layout()
        
        output_path = self.output_dir / "delay_distribution.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Delay distribution saved to {output_path}")
        return str(output_path)
    
    def analyze_weather_impact(self) -> str:
        """
        Analyze impact of weather on delays (FR-15)
        
        Returns:
            Path to saved visualization
        """
        logger.info("Analyzing weather impact on delays...")
        
        if 'weather' not in self.df.columns or 'delay_minutes' not in self.df.columns:
            logger.warning("Required columns missing for weather analysis")
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Weather Impact on Delays', fontsize=16, fontweight='bold')
        
        # Box plot by weather
        weather_order = ['clear', 'cloudy', 'rainy', 'snowy']
        available_weather = [w for w in weather_order if w in self.df['weather'].values]
        
        data_for_plot = [self.df[self.df['weather'] == w]['delay_minutes'].values 
                        for w in available_weather]
        
        axes[0].boxplot(data_for_plot, labels=available_weather)
        axes[0].set_title('Delay by Weather Condition')
        axes[0].set_xlabel('Weather')
        axes[0].set_ylabel('Delay (minutes)')
        axes[0].grid(True, alpha=0.3)
        
        # Bar plot of mean delays
        mean_delays = self.df.groupby('weather')['delay_minutes'].mean().sort_values()
        mean_delays.plot(kind='bar', ax=axes[1], color='steelblue', edgecolor='black')
        axes[1].set_title('Mean Delay by Weather')
        axes[1].set_xlabel('Weather')
        axes[1].set_ylabel('Mean Delay (minutes)')
        axes[1].grid(True, alpha=0.3, axis='y')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        output_path = self.output_dir / "weather_impact.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Weather impact analysis saved to {output_path}")
        return str(output_path)
    
    def analyze_time_of_day_impact(self) -> str:
        """
        Analyze relationship between time of day and delays (FR-16)
        
        Returns:
            Path to saved visualization
        """
        logger.info("Analyzing time of day impact on delays...")
        
        if 'time_of_day' not in self.df.columns or 'delay_minutes' not in self.df.columns:
            logger.warning("Required columns missing for time analysis")
            return None
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Time of Day Impact on Delays', fontsize=16, fontweight='bold')
        
        # Map time_of_day to labels
        time_labels = {0: 'Morning (6-12)', 1: 'Afternoon (12-18)', 
                      2: 'Evening (18-24)', 3: 'Night (0-6)'}
        self.df['time_label'] = self.df['time_of_day'].map(time_labels)
        
        # Box plot
        time_order = [time_labels[i] for i in sorted(self.df['time_of_day'].unique())]
        data_for_plot = [self.df[self.df['time_label'] == t]['delay_minutes'].values 
                        for t in time_order]
        
        axes[0].boxplot(data_for_plot, labels=time_order)
        axes[0].set_title('Delay by Time of Day')
        axes[0].set_xlabel('Time of Day')
        axes[0].set_ylabel('Delay (minutes)')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)
        
        # Line plot of mean delays
        mean_delays = self.df.groupby('time_of_day')['delay_minutes'].mean().sort_index()
        mean_delays.plot(kind='line', ax=axes[1], marker='o', linewidth=2, markersize=8)
        axes[1].set_title('Mean Delay by Time of Day')
        axes[1].set_xlabel('Time of Day')
        axes[1].set_ylabel('Mean Delay (minutes)')
        axes[1].set_xticks(range(4))
        axes[1].set_xticklabels([time_labels[i] for i in range(4)], rotation=45, ha='right')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_path = self.output_dir / "time_of_day_impact.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Time of day analysis saved to {output_path}")
        return str(output_path)
    
    def generate_all_visualizations(self) -> dict:
        """
        Generate all EDA visualizations
        
        Returns:
            Dictionary of visualization paths
        """
        logger.info("Generating all EDA visualizations...")
        
        visualizations = {}
        
        visualizations['delay_distribution'] = self.visualize_delay_distribution()
        visualizations['weather_impact'] = self.analyze_weather_impact()
        visualizations['time_of_day_impact'] = self.analyze_time_of_day_impact()
        
        logger.info(f"Generated {len(visualizations)} visualizations")
        
        return visualizations

