

CREATE DATABASE IF NOT EXISTS frota_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE frota_db;


CREATE TABLE TBL_VEICULO (
    vei_codigo          INT AUTO_INCREMENT,
    vei_placa           VARCHAR(8)      NOT NULL,
    vei_modelo          VARCHAR(50)     NOT NULL,
    vei_ano             SMALLINT        NOT NULL,
    vei_quilometragem   DECIMAL(10,2)   NOT NULL,
    vei_criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vei_atualizado_em   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_veiculo PRIMARY KEY (vei_codigo),
    CONSTRAINT uq_veiculo_placa UNIQUE (vei_placa),
    CONSTRAINT ck_veiculo_ano CHECK (vei_ano >= 1950),
    CONSTRAINT ck_veiculo_km CHECK (vei_quilometragem >= 0)
);


CREATE TABLE TBL_MOTORISTA (
    mot_codigo    INT AUTO_INCREMENT,
    mot_cnh       VARCHAR(11)  NOT NULL,
    mot_nome      VARCHAR(100) NOT NULL,
    mot_categoria VARCHAR(2)   NOT NULL,
    mot_telefone  VARCHAR(20)  NOT NULL,
    mot_ativo     TINYINT(1)   NOT NULL DEFAULT 1,
    CONSTRAINT pk_motorista PRIMARY KEY (mot_codigo),
    CONSTRAINT uq_motorista_cnh UNIQUE (mot_cnh),
    CONSTRAINT ck_motorista_categoria CHECK (mot_categoria IN ('A','B','AB','C','D','E'))
);


CREATE TABLE TBL_MECANICO (
    mec_codigo        INT AUTO_INCREMENT,
    mec_nome          VARCHAR(100) NOT NULL,
    mec_especialidade VARCHAR(50)  NOT NULL,
    mec_turno         VARCHAR(10)  NOT NULL,
    mec_ativo         TINYINT(1)   NOT NULL DEFAULT 1,
    CONSTRAINT pk_mecanico PRIMARY KEY (mec_codigo),
    CONSTRAINT ck_mecanico_turno CHECK (mec_turno IN ('MANHA','TARDE','NOITE'))
);

CREATE TABLE TBL_PECA (
    pec_codigo        INT AUTO_INCREMENT,
    pec_nome          VARCHAR(100)  NOT NULL,
    pec_fabricante    VARCHAR(100)  NOT NULL,
    pec_valor         DECIMAL(10,2) NOT NULL,
    pec_qtd_estoque   INT           NOT NULL DEFAULT 0,
    pec_estoque_minimo INT          NOT NULL DEFAULT 5,
    CONSTRAINT pk_peca PRIMARY KEY (pec_codigo),
    CONSTRAINT ck_peca_valor CHECK (pec_valor > 0),
    CONSTRAINT ck_peca_estoque CHECK (pec_qtd_estoque >= 0),
    CONSTRAINT ck_peca_estoque_minimo CHECK (pec_estoque_minimo >= 0)
);

CREATE TABLE TBL_MANUTENCAO (
    man_codigo    INT AUTO_INCREMENT,
    man_data      DATE         NOT NULL,
    man_tipo      VARCHAR(15)  NOT NULL,
    man_descricao TEXT         NOT NULL,
    vei_codigo    INT          NOT NULL,
    mec_codigo    INT          NOT NULL,
    CONSTRAINT pk_manutencao PRIMARY KEY (man_codigo),
    CONSTRAINT fk_manutencao_veiculo FOREIGN KEY (vei_codigo)
        REFERENCES TBL_VEICULO (vei_codigo) ON DELETE CASCADE,
    CONSTRAINT fk_manutencao_mecanico FOREIGN KEY (mec_codigo)
        REFERENCES TBL_MECANICO (mec_codigo) ON DELETE CASCADE,
    CONSTRAINT ck_manutencao_tipo CHECK (man_tipo IN ('PREVENTIVA','CORRETIVA'))
);


CREATE TABLE TBL_ITEM_MANUTENCAO (
    ite_codigo         INT AUTO_INCREMENT,
    ite_quantidade     INT           NOT NULL,
    ite_valor_unitario DECIMAL(10,2) NOT NULL,
    man_codigo         INT           NOT NULL,
    pec_codigo         INT           NOT NULL,
    CONSTRAINT pk_item_manutencao PRIMARY KEY (ite_codigo),
    CONSTRAINT fk_item_manutencao_manutencao FOREIGN KEY (man_codigo)
        REFERENCES TBL_MANUTENCAO (man_codigo) ON DELETE CASCADE,
    CONSTRAINT fk_item_manutencao_peca FOREIGN KEY (pec_codigo)
        REFERENCES TBL_PECA (pec_codigo) ON DELETE RESTRICT,
    CONSTRAINT ck_item_quantidade CHECK (ite_quantidade > 0),
    CONSTRAINT ck_item_valor CHECK (ite_valor_unitario > 0)
);


CREATE INDEX idx_manutencao_data ON TBL_MANUTENCAO (man_data);
CREATE INDEX idx_item_manutencao_peca ON TBL_ITEM_MANUTENCAO (pec_codigo);
