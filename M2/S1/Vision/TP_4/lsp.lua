return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        rust_analyzer = {},
        nil_ls = {},
		rnix-lsp = {},
		texlab = {},
		pyright = {},
      },
    },
  },
}
