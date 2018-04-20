function editarSenha(id, usuario, senha, url, descricao, idUsuario) {
    $('#usuario').val(usuario);
    $('#senha').val(senha);
    $('#url').val(url);
    $('#descricao').val(descricao);
    $('#modalSenha').modal('show');
}

function limparCampos() {
    $('#usuario').val('');
    $('#senha').val('');
    $('#url').val('');
    $('#descricao').val('');
    $('#modalSenha').modal('show');
}