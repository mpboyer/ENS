use std::ops::Deref;

/// Wrapper type to allow flexible source input
pub struct Sources(pub Vec<usize>);

impl From<usize> for Sources {
    fn from(source: usize) -> Self {
        Sources(vec![source])
    }
}

impl From<Vec<usize>> for Sources {
    fn from(sources: Vec<usize>) -> Self {
        Sources(sources)
    }
}

impl From<&[usize]> for Sources {
    fn from(sources: &[usize]) -> Self {
        Sources(sources.to_vec())
    }
}

impl<const N: usize> From<[usize; N]> for Sources {
    fn from(sources: [usize; N]) -> Self {
        Sources(sources.to_vec())
    }
}

impl Deref for Sources {
    type Target = Vec<usize>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}
