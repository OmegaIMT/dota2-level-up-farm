import os
from PIL import Image
from rembg import remove
import argparse

def remover_fundo_imagem(input_path, output_path):
    """Remove o fundo de uma imagem e salva o resultado"""
    try:
        # Abrir a imagem
        imagem_original = Image.open(input_path)
        
        # Remover o fundo
        imagem_sem_fundo = remove(imagem_original)
        
        # Salvar a imagem resultante
        imagem_sem_fundo.save(output_path)
        print(f"Sucesso: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"Erro ao processar {input_path}: {str(e)}")
        return False

def processar_pasta(pasta_origem, pasta_destino=None, formato="png"):
    """Processa todas as imagens de uma pasta"""
    # Se não for especificada uma pasta de destino, usar uma subpasta
    if pasta_destino is None:
        pasta_destino = os.path.join(pasta_origem, "sem_fundo")
    
    # Criar a pasta de destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta criada: {pasta_destino}")
    
    # Formatos de imagem suportados
    formatos_suportados = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # Contadores para estatísticas
    total = 0
    sucessos = 0
    
    # Processar cada arquivo na pasta
    for arquivo in os.listdir(pasta_origem):
        nome, extensao = os.path.splitext(arquivo)
        
        if extensao.lower() in formatos_suportados:
            total += 1
            caminho_origem = os.path.join(pasta_origem, arquivo)
            nome_saida = f"{nome}_sem_fundo.{formato}"
            caminho_destino = os.path.join(pasta_destino, nome_saida)
            
            if remover_fundo_imagem(caminho_origem, caminho_destino):
                sucessos += 1
    
    # Relatório final
    print(f"\nProcessamento concluído!")
    print(f"Total de imagens processadas: {total}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {total - sucessos}")
    print(f"Imagens sem fundo salvas em: {pasta_destino}")

if __name__ == "__main__":
    # Configurar parser de argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Remover fundo de imagens em uma pasta')
    parser.add_argument('pasta_origem', help='Caminho para a pasta com as imagens originais')
    parser.add_argument('--destino', '-d', help='Caminho para salvar as imagens processadas (opcional)')
    parser.add_argument('--formato', '-f', default='png', choices=['png', 'jpg', 'webp'], 
                       help='Formato de saída (padrão: png)')
    
    args = parser.parse_args()
    
    # Verificar se a pasta de origem existe
    if not os.path.isdir(args.pasta_origem):
        print(f"Erro: A pasta '{args.pasta_origem}' não existe!")
        exit(1)
    
    # Executar o processamento
    processar_pasta(args.pasta_origem, args.destino, args.formato)