

#PROJECT REPORT

##







##POSIBLE ACTIONS
    - (FET) Precalcular a l'__init__ loss_matrix, customer_gain i plant_switch_cost perquè result() calculi el valor incremental.
    - Possible millora: guardar a l'estat un comptador de clients per central (enters) en lloc de mirar si està buida amb l'energia lliure i una tolerància.








##OBSERVATIONS

Del codi donat, nomès s'ha alterat el mètode __repr__ de les classes donades per tal de facilitar mes la visualització de les instàncies

22.10.2026
He arreglat alguna cosa dels imports per a tenir un fix temporal mentre seguim treballant amb l'estructura de code/ i given_code/. Després s'haurà de treure.
    sys path etc... de problem.py

He afegit al init de problema una crida a compute supply, que diu quants mw hauria d'enviar cada central a cada client tenint en compte les perdues de les distancies. Un càlcul que només es fa a l'inici i no es torna a fer i aixi ho tenm cpm a consulta directa. Falta completar la funció del càlcul: _compute_supply
