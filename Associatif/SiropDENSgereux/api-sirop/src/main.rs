#[derive(Debug, Copy, Clone)]
pub enum Sirop {
    Anis,
    BananeVerte,
    Barbapapa,
    Basilic,
    BonbonFraise,
    CanneASucre,
    Caramel,
    Cassis,
    Citron,
    CitronRior,
    Coco,
    Concombre,
    Coquelicot,
    Cranberry,
    CrumblePomme,
    Curaçao,
    Fraise,
    FraiseDesBois,
    Gingembre,
    Grenadine,
    Kiwi,
    Mandarine,
    Melon,
    MentheVerte,
    MentheGlaciale,
    Mîre,
    Noisette,
    Orange,
    Orgeat,
    Passion,
    Pêche,
    PêcheAbricot,
    Poire,
    PommeRouge,
    PommeVerte,
    Speculoos,
    ThéPêche,
    Vanille,
    VinChaud,
    Violette,
}

#[derive(Debug, Copy, Clone)]
pub enum Ingrédient {
    Coca,
    Eau,
    Lait,
    Sirop(Sirop),
}

#[derive(Debug, Clone)]
pub enum Opération {
    Mélange(Vec<Boisson>),
    Mousser,
    Prélever,
}

#[derive(Debug, Clone)]
pub struct Boisson {
    nom: [u8; 256],
    ingrédients: Vec<Ingrédient>,
    recette: Vec<Opération>,
}

impl Boisson {
    pub fn new(
        nom: [u8; 256], ingrédients: Vec<Ingrédient>, recette: Vec<Opération>
    ) -> Boisson {
        Boisson {
            ingrédients,
            nom,
            recette,
        }
    }

    pub fn ingrédients(self) -> Vec<Ingrédient> {
        self.ingrédients
    }

    pub fn recette(self) -> Vec<Opération> {
        self.recette
    }

    pub fn howto(self) -> () {}
}

#[derive(Debug, Copy, Clone)]
pub enum Note {
    Torture,
    Cancérigène,
    Dangereux,
    Horrifiant,
    Honteux,
    Mauvais,
    Médiocre,
    Passable,
    Buvable,
    Rafraichissant,
}

fn main() {
    println!("Hello, world!");
}
