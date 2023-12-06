# Construction d'un processeur

## Instructions à prévoir :
On maintient au moins 8 registres.
Pour tous deux registres r1, r2. On veut maintenir :
    - r1 <- r1 + r2 (pour tout opérateur +)
    - r1 <- RAM\[r2 + c\]
    - RAM\[r2 + c\] <- r1
    - jump to r2 if r1 = 0

Il suffit de simuler une instruction par cycle.




## Registres :
Il y a plusieurs niveaux de cache possibles dans le processeur et différentes tailles de registres.

### Registre à un bit :
3 fils d'entrée : WData, WEnable et un troisième fil dans lequel on met la sortie du registre. On envoie l'input dans un multiplexer. On met la sortie dans RData.

### Généralisation :
Pour un registre à plusieurs bits, on duplique des registres à un bit. On sépare le bus d'entrée dans les registres correspondants. On envoie dans le canal WEnable de chaque registre une même valeur W d'entrée. On transforme RData en un bus. 

### Ecriture
On utilise un démultiplexer dont toutes les sorties sont nulles sauf celle de l'adresse choisie pour définir le registre dans lequel on va écrire.

### Lecture
On utilise un multiplexer à n entrées et on prend celle égale au registre de l'adresse de lecture.

### Multiplexer et Démultiplexer à n bits
On le construit récursivement en appliquant le k-ème bit sur 2^k multiplexers/démultiplexers.




## Le Processeur en lui-même

### Composants Principaux
    - Bloc RAM
    - Bloc Registre (REG)
    - Bloc d'Instructions (INSTR)
    - Bloc ALU

### Bloc ALU
Prend deux valeurs en entrée, une opération et une sortie.

### Opérations
#### Application d'Opérateur
INSTR donne à REG les adresses et on donne les registres en entrée à l'ALU. A partir de l'opérateur donné à l'ALU, on envoie le résultat dans le WData de REG, qui l'enregistre à partir de WAddr et de WEnable. 

#### Enregistrement en Registre
On utilise un multiplexer en entrée et en sortie de ALU. 

#### Enregistrement en RAM
On récupère la sortie de REG et on l'envoie en WData de RAM avec comme adresse le résultat d'une opération rapide de ALU. 

#### Jump
On modifie l'IAddress du bloc INSTR en la faisant passer dans un registre avec un multiplexer en sortie selon le résultat d'une opération de test de la valeur de r1 de l'ALU.





