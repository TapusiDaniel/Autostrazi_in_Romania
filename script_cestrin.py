import requests
import json
from datetime import datetime

def alternative_queries():
    """
    Try different query approaches for the CLUJ-DEJ project
    """
    base_url = "https://utility.arcgis.com/usrsvcs/servers/a55600f1d1aa482ab17fa5f0691587b4/rest/services/ProgramConstructie/FeatureServer/0"
    
    headers = {
        'Referer': 'https://cestrin.maps.arcgis.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # Different query variations to try
    queries = [
        {
            'name': 'CLUJ substring search',
            'where': "indicativ_drum LIKE '%CLUJ%'"
        },
        {
            'name': 'DEJ substring search', 
            'where': "indicativ_drum LIKE '%DEJ%'"
        },
        {
            'name': 'Express road category',
            'where': "rang_drum = 'DRUM EXPRES'"
        },
        {
            'name': 'Express road preparation phase',
            'where': "categorie_drum LIKE '%DRUMURI EXPRES IN PREGATIRE%'"
        },
        {
            'name': 'All express roads',
            'where': "categorie_drum LIKE '%EXPRES%'"
        }
    ]
    
    for query in queries:
        try:
            print(f"\nTrying: {query['name']}")
            params = {
                'where': query['where'],
                'outFields': 'indicativ_drum,categorie_drum,rang_drum,lungime_km,stadiu_actual_fizic,data_inceperii,data_finalizarii,valoare_proiect,antreprenor',
                'f': 'json',
                'outSR': '4326',
                'resultRecordCount': 10
            }
            
            response = requests.get(f"{base_url}/query", params=params, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                print(f"✓ Found {len(features)} features")
                
                for feature in features:
                    attrs = feature.get('attributes', {})
                    indicativ = attrs.get('indicativ_drum', 'N/A')
                    categorie = attrs.get('categorie_drum', 'N/A')
                    print(f"  - {indicativ}: {categorie}")
                    
                    # Check if this is our CLUJ-DEJ road
                    if 'CLUJ' in str(indicativ).upper() and 'DEJ' in str(indicativ).upper():
                        print(f"  *** FOUND CLUJ-DEJ PROJECT! ***")
                        # Save this feature
                        filename = f"cluj_dej_project_{datetime.now().strftime('%Y%m%d')}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(feature, f, ensure_ascii=False, indent=2)
                        print(f"  Saved to: {filename}")
                        
            else:
                print(f"✗ Failed: {response.status_code}")
                if response.status_code == 403:
                    print("  Still getting 403 Forbidden")
                    
        except Exception as e:
            print(f"✗ Error: {e}")

# Run alternative queries
alternative_queries()