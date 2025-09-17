#!/usr/bin/env python3
"""
Main script för IGDB data collection och ETL
Kör fullständig pipeline från data collection till ML-ready format
"""

import sys
import argparse
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_collectors.igdb_data_collector import IGDBDataCollector
from data_processing.etl_pipeline import IGDBETLPipeline
from data_processing.data_validator import IGDBDataValidator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Huvudfunktion för data collection pipeline"""
    parser = argparse.ArgumentParser(description='IGDB Data Collection Pipeline')
    parser.add_argument('--games-limit', type=int, default=1000, 
                       help='Antal spel att hämta (default: 1000)')
    parser.add_argument('--skip-collection', action='store_true',
                       help='Hoppa över data collection, kör endast ETL')
    parser.add_argument('--skip-etl', action='store_true',
                       help='Hoppa över ETL, kör endast data collection')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Hoppa över data validation')
    
    args = parser.parse_args()
    
    logger.info("Börjar IGDB data collection pipeline")
    logger.info(f"Games limit: {args.games_limit}")
    
    try:
        # Steg 1: Data Collection
        if not args.skip_collection:
            logger.info("=" * 50)
            logger.info("STEG 1: DATA COLLECTION")
            logger.info("=" * 50)
            
            collector = IGDBDataCollector()
            saved_files = collector.collect_all_data(games_limit=args.games_limit)
            
            if not saved_files:
                logger.error("Data collection misslyckades")
                return 1
            
            logger.info("Data collection klar")
        else:
            logger.info("Hoppar över data collection")
        
        # Steg 2: ETL Pipeline
        if not args.skip_etl:
            logger.info("=" * 50)
            logger.info("STEG 2: ETL PIPELINE")
            logger.info("=" * 50)
            
            pipeline = IGDBETLPipeline()
            etl_result = pipeline.run_full_etl()
            
            if not etl_result:
                logger.error("ETL pipeline misslyckades")
                return 1
            
            logger.info("ETL pipeline klar")
        else:
            logger.info("Hoppar över ETL pipeline")
        
        # Steg 3: Data Validation
        if not args.skip_validation:
            logger.info("=" * 50)
            logger.info("STEG 3: DATA VALIDATION")
            logger.info("=" * 50)
            
            validator = IGDBDataValidator()
            
            # Ladda processad data för validation
            processed_files = list(validator.processed_dir.glob("games_*.csv"))
            if processed_files:
                latest_file = max(processed_files, key=lambda x: x.stat().st_mtime)
                import pandas as pd
                df = pd.read_csv(latest_file)
                
                report_file = validator.save_validation_report(df)
                logger.info(f"Validation report sparad till {report_file}")
            else:
                logger.warning("Ingen processad data hittades för validation")
        else:
            logger.info("Hoppar över data validation")
        
        logger.info("=" * 50)
        logger.info("PIPELINE KLAR!")
        logger.info("=" * 50)
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline misslyckades: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
