import os
import json
import logging
from typing import Dict, List

def validate_contracts(contracts_dir: str) -> Dict[str, List[str]]:
    """Valida todos los contratos generados"""
    results = {
        "valid": [],
        "invalid": [],
        "errors": []
    }
    
    for root, _, files in os.walk(contracts_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contract = json.load(f)
                        
                    # Validar estructura básica
                    if not all(k in contract for k in ["metadata", "source_information"]):
                        results["invalid"].append(f"{file}: Falta estructura básica")
                        continue
                        
                    # Validar campos completos
                    metadata = contract["metadata"].get("validation", {})
                    if not metadata.get("is_complete", False):
                        results["invalid"].append(
                            f"{file}: Campos incompletos ({metadata.get('processed_fields', 0)} de {metadata.get('total_fields', 0)})"
                        )
                        continue
                        
                    results["valid"].append(file)
                    
                except Exception as e:
                    results["errors"].append(f"{file}: {str(e)}")
                    
    return results

if __name__ == "__main__":
    results = validate_contracts("contracts")
    print("\nResultados de validación:")
    print(f"Contratos válidos: {len(results['valid'])}")
    print(f"Contratos inválidos: {len(results['invalid'])}")
    print(f"Errores: {len(results['errors'])}")
    
    if results["invalid"]:
        print("\nContratos inválidos:")
        for inv in results["invalid"]:
            print(f"- {inv}")
            
    if results["errors"]:
        print("\nErrores encontrados:")
        for err in results["errors"]:
            print(f"- {err}") 