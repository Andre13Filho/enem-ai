"""
Exemplo de como implementar Fine Tuning para matemática
ATENÇÃO: Este é apenas um exemplo conceitual - requer recursos significativos
"""

from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import torch
from pathlib import Path
import json

class MathFineTuner:
    """Sistema de Fine Tuning para matemática - EXEMPLO CONCEITUAL"""
    
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        """
        IMPORTANTE: Modelos maiores requerem muito mais recursos
        Para resultados reais, considere: 
        - "meta-llama/Llama-2-7b-hf" (precisa de aprovação)
        - "microsoft/DialoGPT-large"
        - "EleutherAI/gpt-neo-1.3B"
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def prepare_training_data(self, math_folder="./matemática"):
        """Prepara dados de treinamento dos documentos de matemática"""
        training_examples = []
        
        # Processa documentos da pasta matemática
        for file_path in Path(math_folder).glob("*.docx"):
            try:
                # Extrai conteúdo (você já tem essa função)
                content = self._extract_docx_content(file_path)
                
                # Cria exemplos de pergunta-resposta
                examples = self._create_qa_pairs(content, file_path.stem)
                training_examples.extend(examples)
                
            except Exception as e:
                print(f"Erro processando {file_path}: {e}")
        
        return training_examples
    
    def _create_qa_pairs(self, content, topic):
        """Cria pares pergunta-resposta para treinamento"""
        examples = []
        
        # Exemplo de como criar dados de treinamento
        # Na prática, seria muito mais sofisticado
        sections = content.split('\n\n')
        
        for section in sections:
            if len(section) > 100:  # Apenas seções substanciais
                examples.append({
                    "input": f"Explique sobre {topic}:",
                    "output": section.strip(),
                    "topic": topic
                })
                
                # Variações de perguntas
                examples.append({
                    "input": f"Como resolver exercícios de {topic}?",
                    "output": f"Para resolver {topic}, considere: {section[:200]}...",
                    "topic": topic
                })
        
        return examples
    
    def fine_tune_model(self, training_data, output_dir="./fine_tuned_math_model"):
        """Executa o fine tuning - REQUER RECURSOS SIGNIFICATIVOS"""
        
        print("🚀 Iniciando Fine Tuning...")
        print(f"📊 {len(training_data)} exemplos de treinamento")
        print(f"💻 Dispositivo: {self.device}")
        
        # 1. Carrega modelo e tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Adiciona token de padding se necessário
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 2. Prepara dataset
        dataset = self._prepare_dataset(training_data)
        
        # 3. Configurações de treinamento
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,  # ATENÇÃO: Pode levar horas/dias
            per_device_train_batch_size=2,  # Pequeno para não estourar memória
            gradient_accumulation_steps=4,
            warmup_steps=100,
            learning_rate=5e-5,
            save_steps=500,
            logging_steps=100,
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
        )
        
        # 4. Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal LM, não masked LM
        )
        
        # 5. Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset,
        )
        
        # 6. EXECUTA O TREINAMENTO - PODE LEVAR MUITO TEMPO
        print("⚠️  ATENÇÃO: Treinamento pode levar horas ou dias dependendo do hardware")
        trainer.train()
        
        # 7. Salva modelo fine-tunado
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"✅ Fine tuning concluído! Modelo salvo em: {output_dir}")
        
    def _prepare_dataset(self, training_data):
        """Prepara dataset para o Trainer"""
        def tokenize_function(examples):
            # Combina input e output para treinamento causal
            texts = [f"Pergunta: {inp}\nResposta: {out}" 
                    for inp, out in zip(examples['input'], examples['output'])]
            
            return self.tokenizer(
                texts, 
                truncation=True, 
                padding=True, 
                max_length=512,
                return_tensors="pt"
            )
        
        # Converte para formato Dataset
        dataset_dict = {
            'input': [ex['input'] for ex in training_data],
            'output': [ex['output'] for ex in training_data]
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def load_fine_tuned_model(self, model_path="./fine_tuned_math_model"):
        """Carrega modelo fine-tunado"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.model.to(self.device)
        
    def generate_response(self, question, max_length=200):
        """Gera resposta usando modelo fine-tunado"""
        if not self.model or not self.tokenizer:
            raise ValueError("Modelo não carregado. Use load_fine_tuned_model() primeiro.")
        
        prompt = f"Pergunta: {question}\nResposta:"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove o prompt da resposta
        response = response.replace(prompt, "").strip()
        
        return response

# EXEMPLO DE USO (CONCEITUAL)
def exemplo_fine_tuning():
    """Exemplo de como usar o sistema de fine tuning"""
    
    print("🔧 EXEMPLO DE FINE TUNING - APENAS DEMONSTRAÇÃO")
    print("⚠️  REQUER: GPU potente, muito tempo, e dados bem formatados")
    
    # 1. Inicializa fine tuner
    tuner = MathFineTuner()
    
    # 2. Prepara dados (se você ainda tiver a pasta matemática)
    # training_data = tuner.prepare_training_data("./matemática")
    
    # 3. Dados de exemplo (simulado)
    training_data = [
        {
            "input": "Como calcular juros compostos?",
            "output": "Para calcular juros compostos, use a fórmula M = C(1+i)^t, onde M é montante, C é capital, i é taxa e t é tempo.",
            "topic": "Matemática Financeira"
        },
        {
            "input": "O que é uma função quadrática?",
            "output": "Uma função quadrática é do tipo f(x) = ax² + bx + c, onde a ≠ 0. Seu gráfico é uma parábola.",
            "topic": "Funções"
        }
        # ... centenas ou milhares de exemplos seriam necessários
    ]
    
    print(f"📚 Dados preparados: {len(training_data)} exemplos")
    
    # 4. Fine tuning (COMENTADO - muito pesado)
    # tuner.fine_tune_model(training_data)
    
    # 5. Usar modelo fine-tunado
    # tuner.load_fine_tuned_model()
    # response = tuner.generate_response("Como resolver uma equação do segundo grau?")
    # print(f"Resposta: {response}")
    
    print("\n💡 Para implementar de verdade, você precisaria:")
    print("- GPU com pelo menos 8GB VRAM")
    print("- Milhares de exemplos bem formatados") 
    print("- Várias horas/dias de treinamento")
    print("- Expertise em ML para ajustar hiperparâmetros")

if __name__ == "__main__":
    exemplo_fine_tuning() 