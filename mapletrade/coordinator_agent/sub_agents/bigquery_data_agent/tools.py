# coordinator_agent/sub_agents/bigquery_data_agent/tools.py
"""
BigQuery tools for storing and retrieving Canadian market data
"""

from typing import Dict, List, Optional
from google.cloud import bigquery
import os
from datetime import datetime

def store_market_data(symbol: str, data: Dict) -> Dict:
    """
    Store TSX market data in BigQuery.
    
    Args:
        symbol: Stock symbol (e.g., 'TD.TO')
        data: Market data dictionary
        
    Returns:
        Storage confirmation with table info
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        dataset_id = 'mapletrade_data'
        table_id = 'market_data'
        
        client = bigquery.Client(project=project_id)
        
        # Prepare row for BigQuery
        row = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price': data.get('price'),
            'volume': data.get('volume'),
            'market_cap': data.get('market_cap'),
            'source': data.get('source', 'Unknown')
        }
        
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)
        
        errors = client.insert_rows_json(table, [row])
        
        if errors:
            return {
                "error": f"Failed to store data: {errors}",
                "symbol": symbol
            }
        
        return {
            "success": True,
            "symbol": symbol,
            "table": f"{project_id}.{dataset_id}.{table_id}",
            "row_count": 1,
            "educational_note": "📊 Data stored in BigQuery for historical analysis and trend tracking"
        }
        
    except Exception as e:
        return {
            "error": f"BigQuery storage failed: {str(e)}",
            "symbol": symbol,
            "fallback": "Data not persisted - using in-memory storage"
        }

def query_historical_data(symbol: str, days: int = 30) -> Dict:
    """
    Query historical market data from BigQuery.
    
    Args:
        symbol: Stock symbol  
        days: Number of days to retrieve
        
    Returns:
        Historical data with trend analysis
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        client = bigquery.Client(project=project_id)
        
        query = f"""
        SELECT 
            symbol,
            timestamp,
            price,
            volume,
            source
        FROM `{project_id}.mapletrade_data.market_data`
        WHERE symbol = @symbol
        AND timestamp >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL @days DAY)
        ORDER BY timestamp DESC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                bigquery.ScalarQueryParameter("days", "INT64", days)
            ]
        )
        
        results = client.query(query, job_config=job_config)
        rows = list(results)
        
        if not rows:
            return {
                "symbol": symbol,
                "message": f"No historical data found for {symbol} in last {days} days",
                "data_count": 0,
                "suggestion": "Try collecting data first using the data collection agent"
            }
        
        # Process results
        data_points = []
        for row in rows:
            data_points.append({
                "timestamp": row.timestamp.isoformat(),
                "price": float(row.price) if row.price else None,
                "volume": int(row.volume) if row.volume else None,
                "source": row.source
            })
        
        return {
            "symbol": symbol,
            "period_days": days,
            "data_count": len(data_points),
            "historical_data": data_points,
            "query_info": {
                "table": f"{project_id}.mapletrade_data.market_data",
                "query_timestamp": datetime.now().isoformat()
            },
            "educational_notes": [
                "📈 Historical data enables trend analysis and pattern recognition",
                "📊 BigQuery automatically handles data warehousing and analytics",
                "💡 Use this data for backtesting trading strategies"
            ]
        }
        
    except Exception as e:
        return {
            "error": f"BigQuery query failed: {str(e)}",
            "symbol": symbol,
            "alternative": "Use data collection agent for real-time data"
        }

def setup_bigquery_tables() -> Dict:
    """
    Create BigQuery dataset and tables for MapleTrade.
    
    Returns:
        Setup confirmation and table schema info
    """
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        dataset_id = 'mapletrade_data'
        
        client = bigquery.Client(project=project_id)
        
        # Create dataset
        dataset_ref = client.dataset(dataset_id)
        try:
            client.get_dataset(dataset_ref)
            dataset_exists = True
        except:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset.description = "MapleTrade Canadian market data storage"
            client.create_dataset(dataset)
            dataset_exists = False
        
        # Create market_data table
        table_ref = dataset_ref.table('market_data')
        try:
            client.get_table(table_ref)
            table_exists = True
        except:
            schema = [
                bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "DATETIME", mode="REQUIRED"),
                bigquery.SchemaField("price", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("volume", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("market_cap", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("source", "STRING", mode="NULLABLE")
            ]
            
            table = bigquery.Table(table_ref, schema=schema)
            table.description = "Real-time TSX market data"
            client.create_table(table)
            table_exists = False
        
        return {
            "success": True,
            "dataset": f"{project_id}.{dataset_id}",
            "tables_created": {
                "market_data": f"{project_id}.{dataset_id}.market_data"
            },
            "status": {
                "dataset_existed": dataset_exists,
                "table_existed": table_exists
            },
            "educational_info": [
                "🗄️ BigQuery dataset ready for Canadian market data",
                "📋 Schema optimized for TSX stock tracking",
                "🔍 Ready for SQL queries and trend analysis"
            ]
        }
        
    except Exception as e:
        return {
            "error": f"BigQuery setup failed: {str(e)}",
            "manual_setup": "Create dataset 'mapletrade_data' in BigQuery console"
        }