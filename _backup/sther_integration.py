import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from math_exercises_database_creator import EnemMathDatabase, MathTopic

class StherIntegration:
    """Sistema de integração para enviar exercícios de matemática para a Sther"""
    
    def __init__(self):
        self.db = EnemMathDatabase()
        
    def create_exercise_package_for_sther(self, 
                                         topic: Optional[str] = None,
                                         year: Optional[int] = None,
                                         limit: int = 10,
                                         package_name: str = "Exercícios de Matemática") -> Dict:
        """
        Cria um pacote de exercícios formatado para a Sther
        
        Args:
            topic: Tópico específico (opcional)
            year: Ano específico (opcional)
            limit: Número máximo de exercícios
            package_name: Nome do pacote
            
        Returns:
            Dict com os exercícios formatados para a Sther
        """
        
        exercises = []
        
        if topic:
            exercises = self.db.get_exercises_by_topic(topic)
        elif year:
            exercises = self.db.get_exercises_by_year(year)
        else:
            # Busca exercícios variados de diferentes tópicos
            exercises = self._get_mixed_exercises(limit)
        
        # Limita o número de exercícios
        exercises = exercises[:limit]
        
        # Formata para a Sther
        sther_package = {
            "package_info": {
                "name": package_name,
                "created_at": datetime.now().isoformat(),
                "total_exercises": len(exercises),
                "source": "ENEM Math Database",
                "filter_applied": {
                    "topic": topic,
                    "year": year,
                    "limit": limit
                }
            },
            "exercises": self._format_exercises_for_sther(exercises),
            "metadata": {
                "topics_included": list(set([ex['topic'] for ex in exercises])),
                "years_included": list(set([ex['year'] for ex in exercises])),
                "difficulty_levels": list(set([ex['difficulty'] for ex in exercises]))
            }
        }
        
        return sther_package
    
    def _format_exercises_for_sther(self, exercises: List[Dict]) -> List[Dict]:
        """Formata exercícios para o formato esperado pela Sther"""
        formatted = []
        
        for exercise in exercises:
            formatted_exercise = {
                "id": exercise['id'],
                "source_info": {
                    "exam": "ENEM",
                    "year": exercise['year'],
                    "question_number": exercise['question_number'],
                    "day": 2,
                    "subject": "Matemática"
                },
                "content": {
                    "statement": exercise['question_text'],
                    "alternatives": [
                        {"letter": chr(65 + i), "text": alt} 
                        for i, alt in enumerate(exercise['alternatives'])
                    ],
                    "correct_answer": exercise['correct_answer'] if exercise['correct_answer'] else None
                },
                "classification": {
                    "topic": exercise['topic'],
                    "difficulty": exercise['difficulty'],
                    "skills_required": self._identify_skills(exercise)
                },
                "teaching_notes": {
                    "solution_explanation": exercise.get('solution_explanation', ''),
                    "teaching_tips": self._generate_teaching_tips(exercise),
                    "common_mistakes": self._identify_common_mistakes(exercise)
                }
            }
            
            formatted.append(formatted_exercise)
        
        return formatted
    
    def _get_mixed_exercises(self, limit: int) -> List[Dict]:
        """Busca exercícios variados de diferentes tópicos"""
        all_exercises = []
        
        # Busca exercícios de cada tópico principal
        main_topics = ["Geometria", "Funções", "Estatística e Probabilidade", "Álgebra"]
        
        exercises_per_topic = max(1, limit // len(main_topics))
        
        for topic in main_topics:
            topic_exercises = self.db.get_exercises_by_topic(topic)
            all_exercises.extend(topic_exercises[:exercises_per_topic])
        
        # Se ainda precisar de mais exercícios, adiciona outros
        if len(all_exercises) < limit:
            remaining = limit - len(all_exercises)
            other_exercises = self.db.get_exercises_by_topic("Outros")
            all_exercises.extend(other_exercises[:remaining])
        
        return all_exercises[:limit]
    
    def _identify_skills(self, exercise: Dict) -> List[str]:
        """Identifica habilidades necessárias para resolver o exercício"""
        content = (exercise['question_text'] + ' ' + ' '.join(exercise['alternatives'])).lower()
        skills = []
        
        skill_keywords = {
            "interpretação_gráfica": ["gráfico", "eixo", "coordenada", "plotar"],
            "cálculo_numérico": ["calcular", "somar", "multiplicar", "dividir"],
            "resolução_equações": ["equação", "sistema", "resolver", "x ="],
            "geometria_espacial": ["volume", "área superficial", "sólido", "prisma"],
            "análise_dados": ["média", "mediana", "tabela", "dados"],
            "raciocínio_lógico": ["se então", "condição", "implicação", "conclusão"]
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in content for keyword in keywords):
                skills.append(skill.replace("_", " ").title())
        
        return skills if skills else ["Raciocínio Matemático"]
    
    def _generate_teaching_tips(self, exercise: Dict) -> List[str]:
        """Gera dicas de ensino baseadas no exercício"""
        topic = exercise['topic'].lower()
        tips = []
        
        topic_tips = {
            "geometria": [
                "Desenhe a figura para visualizar melhor o problema",
                "Identifique as fórmulas de área e volume necessárias",
                "Verifique as unidades de medida"
            ],
            "funções": [
                "Analise o domínio e imagem da função",
                "Faça um esboço do gráfico se possível",
                "Identifique o tipo de função (linear, quadrática, etc.)"
            ],
            "estatística": [
                "Organize os dados em tabela ou gráfico",
                "Identifique o tipo de medida estatística pedida",
                "Verifique se há valores discrepantes"
            ],
            "álgebra": [
                "Identifique as incógnitas do problema",
                "Monte as equações ou sistema",
                "Verifique a solução substituindo na equação original"
            ]
        }
        
        for key, tip_list in topic_tips.items():
            if key in topic:
                tips.extend(tip_list)
                break
        
        if not tips:
            tips = ["Leia com atenção o enunciado", "Identifique o que está sendo pedido"]
        
        return tips
    
    def _identify_common_mistakes(self, exercise: Dict) -> List[str]:
        """Identifica erros comuns baseados no tipo de exercício"""
        content = exercise['question_text'].lower()
        mistakes = []
        
        if "porcentagem" in content or "%" in content:
            mistakes.append("Confundir aumento/desconto percentual com valor final")
        
        if "área" in content:
            mistakes.append("Confundir fórmulas de área e perímetro")
        
        if "função" in content:
            mistakes.append("Confundir domínio com imagem da função")
        
        if "probabilidade" in content:
            mistakes.append("Não considerar todos os casos possíveis")
        
        if not mistakes:
            mistakes = ["Erro de cálculo", "Interpretação incorreta do enunciado"]
        
        return mistakes
    
    def save_package_for_sther(self, package: Dict, filename: Optional[str] = None) -> str:
        """Salva o pacote em formato JSON para a Sther"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sther_math_package_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def create_topic_packages(self):
        """Cria pacotes separados por tópico para a Sther"""
        stats = self.db.get_statistics()
        created_files = []
        
        for topic, count in stats['by_topic'].items():
            if count >= 5:  # Só cria pacote se tiver pelo menos 5 exercícios
                package = self.create_exercise_package_for_sther(
                    topic=topic,
                    limit=min(20, count),  # Máximo 20 exercícios por pacote
                    package_name=f"Exercícios de {topic}"
                )
                
                filename = self.save_package_for_sther(
                    package, 
                    f"sther_{topic.lower().replace(' ', '_')}.json"
                )
                created_files.append(filename)
                
                print(f"✅ Pacote criado: {filename} ({len(package['exercises'])} exercícios)")
        
        return created_files
    
    def create_yearly_packages(self):
        """Cria pacotes separados por ano para a Sther"""
        stats = self.db.get_statistics()
        created_files = []
        
        for year in stats['by_year'].keys():
            package = self.create_exercise_package_for_sther(
                year=year,
                limit=25,  # Máximo 25 exercícios por ano
                package_name=f"Exercícios ENEM {year}"
            )
            
            filename = self.save_package_for_sther(
                package, 
                f"sther_enem_{year}.json"
            )
            created_files.append(filename)
            
            print(f"✅ Pacote criado: {filename} ({len(package['exercises'])} exercícios)")
        
        return created_files

def main():
    """Função principal para gerar pacotes para a Sther"""
    print("🚀 Iniciando criação de pacotes de exercícios para a Sther...")
    
    integration = StherIntegration()
    
    # Opções do usuário
    print("\nOpções disponíveis:")
    print("1. Criar pacotes por tópico")
    print("2. Criar pacotes por ano")
    print("3. Criar pacote personalizado")
    print("4. Criar todos os tipos")
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    if choice == "1":
        print("\n📚 Criando pacotes por tópico...")
        files = integration.create_topic_packages()
        
    elif choice == "2":
        print("\n📅 Criando pacotes por ano...")
        files = integration.create_yearly_packages()
        
    elif choice == "3":
        print("\n🎯 Criando pacote personalizado...")
        topic = input("Tópico (opcional): ").strip() or None
        year = input("Ano (opcional): ").strip()
        year = int(year) if year.isdigit() else None
        limit = input("Número de exercícios (padrão 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        name = input("Nome do pacote: ").strip() or "Pacote Personalizado"
        
        package = integration.create_exercise_package_for_sther(
            topic=topic, year=year, limit=limit, package_name=name
        )
        filename = integration.save_package_for_sther(package)
        files = [filename]
        
    elif choice == "4":
        print("\n🔄 Criando todos os tipos de pacotes...")
        print("\n📚 Pacotes por tópico:")
        topic_files = integration.create_topic_packages()
        print("\n📅 Pacotes por ano:")
        year_files = integration.create_yearly_packages()
        files = topic_files + year_files
        
    else:
        print("❌ Opção inválida!")
        return
    
    print(f"\n✅ Processamento concluído!")
    print(f"📁 {len(files)} arquivos criados para a Sther:")
    for file in files:
        print(f"   - {file}")
    
    print("\n🎯 Os arquivos estão prontos para serem enviados para a Sther!")

if __name__ == "__main__":
    main() 