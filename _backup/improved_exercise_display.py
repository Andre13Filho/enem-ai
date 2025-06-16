#!/usr/bin/env python3
"""
Sistema de Exibição Melhorado para Exercícios Estruturados
Integra com o parser avançado para mostrar exercícios de forma organizada
"""

import streamlit as st
from typing import List, Dict, Any
import json

from improved_exercise_parser import ExerciseQuestion, Alternative

class ImprovedExerciseDisplay:
    """Classe para exibição otimizada de exercícios estruturados"""
    
    @staticmethod
    def display_structured_exercise(exercise: ExerciseQuestion, exercise_num: int, unique_id: str):
        """
        Exibe um exercício estruturado de forma organizada e elegante
        """
        # Header com informações principais
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <h3 style="margin: 0; font-size: 1.4rem;">
                📝 {exercise.id_questao} - ENEM {exercise.ano}
            </h3>
            <div style="margin-top: 0.8rem; display: flex; flex-wrap: wrap; gap: 1rem;">
                <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">
                    📚 {exercise.area_conhecimento.replace('E SUAS TECNOLOGIAS', '')}
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">
                    🎯 {exercise.dificuldade_estimada}
                </span>
                {f'<span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">🔧 {", ".join(exercise.topicos_chave[:2])}</span>' if exercise.topicos_chave else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Controles de visualização
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        
        with col1:
            show_preview = st.button(
                "👁️ Preview", 
                key=f"preview_{unique_id}",
                help="Ver resumo do exercício"
            )
        
        with col2:
            show_full = st.button(
                "📖 Completo", 
                key=f"full_{unique_id}",
                help="Ver exercício completo"
            )
        
        with col3:
            show_json = st.button(
                "🔧 Estrutura", 
                key=f"json_{unique_id}",
                help="Ver estrutura JSON"
            )
        
        with col4:
            quality_score = ImprovedExerciseDisplay._calculate_quality_score(exercise)
            quality_color = "🟢" if quality_score >= 80 else "🟡" if quality_score >= 60 else "🔴"
            st.markdown(f"**Qualidade:** {quality_color} {quality_score}%")
        
        # Exibição baseada no botão clicado
        if show_preview:
            ImprovedExerciseDisplay._display_preview(exercise)
        
        if show_full:
            ImprovedExerciseDisplay._display_full_exercise(exercise, unique_id)
        
        if show_json:
            ImprovedExerciseDisplay._display_json_structure(exercise)
    
    @staticmethod
    def _display_preview(exercise: ExerciseQuestion):
        """Exibe preview do exercício"""
        st.markdown("#### 👁️ Preview do Exercício")
        
        # Enunciado truncado
        preview_enunciado = exercise.enunciado[:300]
        if len(exercise.enunciado) > 300:
            preview_enunciado += "..."
        
        st.markdown(f"""
        <div style="
            background-color: #f8fafc;
            padding: 1.2rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
        ">
            <h5 style="color: #1e40af; margin-top: 0;">📋 Enunciado</h5>
            <p style="margin-bottom: 1rem;">{preview_enunciado}</p>
            
            <h5 style="color: #1e40af;">📝 Alternativas ({len(exercise.alternativas)} encontradas)</h5>
            <p style="color: #64748b; font-style: italic;">
                Clique em "📖 Completo" para ver todas as alternativas
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _display_full_exercise(exercise: ExerciseQuestion, unique_id: str):
        """Exibe exercício completo com alternativas estruturadas"""
        st.markdown("#### 📖 Exercício Completo")
        
        # Enunciado
        st.markdown(f"""
        <div style="
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        ">
            <h5 style="color: #09278d; margin-top: 0;">📋 Enunciado</h5>
            <div style="line-height: 1.7;">
                {exercise.enunciado}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Alternativas estruturadas
        if exercise.alternativas:
            st.markdown("##### 📝 Alternativas")
            
            for alt in exercise.alternativas:
                # Determina cor baseada na confiança
                confidence_color = "#10b981" if alt.confidence >= 0.8 else "#f59e0b" if alt.confidence >= 0.6 else "#ef4444"
                confidence_emoji = "✅" if alt.confidence >= 0.8 else "⚠️" if alt.confidence >= 0.6 else "❌"
                
                st.markdown(f"""
                <div style="
                    background-color: #f9fafb;
                    padding: 1rem;
                    border-radius: 8px;
                    border-left: 4px solid {confidence_color};
                    margin: 0.5rem 0;
                    display: flex;
                    align-items: flex-start;
                ">
                    <div style="
                        background-color: #09278d;
                        color: white;
                        font-weight: bold;
                        padding: 0.4rem 0.8rem;
                        border-radius: 50%;
                        margin-right: 1rem;
                        min-width: 2rem;
                        text-align: center;
                    ">
                        {alt.letra}
                    </div>
                    <div style="flex: 1;">
                        <div style="line-height: 1.5; margin-bottom: 0.5rem;">
                            {alt.texto if alt.texto else '<em style="color: #9ca3af;">Conteúdo não disponível ou corrompido</em>'}
                        </div>
                        <div style="
                            font-size: 0.8rem;
                            color: #6b7280;
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                        ">
                            {confidence_emoji}
                            <span>Confiança: {int(alt.confidence * 100)}%</span>
                            {'<span style="color: #10b981;">✓ Válida</span>' if alt.is_valid else '<span style="color: #ef4444;">✗ Inválida</span>'}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Nenhuma alternativa foi identificada para esta questão")
        
        # Botões de ação
        ImprovedExerciseDisplay._display_action_buttons(exercise, unique_id)
    
    @staticmethod
    def _display_json_structure(exercise: ExerciseQuestion):
        """Exibe estrutura JSON do exercício"""
        st.markdown("#### 🔧 Estrutura JSON")
        
        # Converte para dicionário e exibe
        exercise_dict = exercise.to_dict()
        
        # Cria versão formatada para exibição
        display_dict = {
            "id_questao": exercise_dict["id_questao"],
            "area_conhecimento": exercise_dict["area_conhecimento"],
            "enunciado": exercise_dict["enunciado"][:100] + "..." if len(exercise_dict["enunciado"]) > 100 else exercise_dict["enunciado"],
            "num_alternativas": len(exercise_dict["alternativas"]),
            "alternativas_validas": sum(1 for alt in exercise_dict["alternativas"] if alt["is_valid"]),
            "topicos_chave": exercise_dict["topicos_chave"],
            "dificuldade_estimada": exercise_dict["dificuldade_estimada"],
            "habilidade_associada": exercise_dict["habilidade_associada"],
            "ano": exercise_dict["ano"],
            "numero_questao": exercise_dict["numero_questao"]
        }
        
        st.json(display_dict)
        
        # Opção para download do JSON completo
        if st.button("💾 Download JSON Completo", key=f"download_{exercise.id_questao}"):
            json_str = exercise.to_json()
            st.download_button(
                label="📄 Baixar JSON",
                data=json_str,
                file_name=f"exercicio_{exercise.numero_questao}_{exercise.ano}.json",
                mime="application/json"
            )
    
    @staticmethod
    def _display_action_buttons(exercise: ExerciseQuestion, unique_id: str):
        """Exibe botões de ação para o exercício"""
        st.markdown("---")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if st.button("💬 Discutir", key=f"discuss_{unique_id}"):
                st.info(f"""
                💬 **Para discutir este exercício:**
                
                Vá para a aba 'Chat' e use esta mensagem:
                
                *"Professor, pode me ajudar com a {exercise.id_questao} do ENEM {exercise.ano}? 
                É sobre {', '.join(exercise.topicos_chave[:2]) if exercise.topicos_chave else 'este tópico'}.
                Tenho dúvida em..."*
                """)
        
        with col_b:
            if st.button("🔗 Conceitos", key=f"concepts_{unique_id}"):
                st.session_state[f"show_concepts_{unique_id}"] = not st.session_state.get(f"show_concepts_{unique_id}", False)
        
        with col_c:
            if st.button("💡 Dicas", key=f"tips_{unique_id}"):
                st.session_state[f"show_tips_{unique_id}"] = not st.session_state.get(f"show_tips_{unique_id}", False)
        
        with col_d:
            if st.button("📊 Análise", key=f"analysis_{unique_id}"):
                st.session_state[f"show_analysis_{unique_id}"] = not st.session_state.get(f"show_analysis_{unique_id}", False)
        
        # Seções expandíveis
        if st.session_state.get(f"show_concepts_{unique_id}", False):
            ImprovedExerciseDisplay._display_concepts(exercise)
        
        if st.session_state.get(f"show_tips_{unique_id}", False):
            ImprovedExerciseDisplay._display_tips(exercise)
        
        if st.session_state.get(f"show_analysis_{unique_id}", False):
            ImprovedExerciseDisplay._display_analysis(exercise)
    
    @staticmethod
    def _display_concepts(exercise: ExerciseQuestion):
        """Exibe conceitos relacionados"""
        st.markdown("#### 🔗 Conceitos Relacionados")
        
        if exercise.topicos_chave:
            for topic in exercise.topicos_chave:
                st.markdown(f"• **{topic.title()}**")
        
        if exercise.habilidade_associada:
            st.markdown(f"• **Habilidade ENEM:** {exercise.habilidade_associada}")
        
        st.markdown(f"• **Área de Conhecimento:** {exercise.area_conhecimento}")
    
    @staticmethod
    def _display_tips(exercise: ExerciseQuestion):
        """Exibe dicas de resolução"""
        st.markdown("#### 💡 Dicas de Resolução")
        
        # Dicas baseadas na dificuldade
        if exercise.dificuldade_estimada == "Fácil":
            st.markdown("💡 **Dica:** Este exercício tem nível básico. Foque na interpretação do enunciado.")
        elif exercise.dificuldade_estimada == "Médio":
            st.markdown("💡 **Dica:** Este exercício requer aplicação de conceitos. Organize os dados fornecidos.")
        else:
            st.markdown("💡 **Dica:** Este exercício é desafiador. Analise cada informação cuidadosamente.")
        
        # Dicas baseadas nos tópicos
        if exercise.topicos_chave:
            topic = exercise.topicos_chave[0]
            topic_tips = {
                'função': '📈 Identifique o tipo de função e analise o gráfico se fornecido.',
                'geometria': '📐 Desenhe a figura e identifique as fórmulas necessárias.',
                'trigonometria': '📐 Lembre-se das relações básicas: SOH-CAH-TOA.',
                'probabilidade': '🎲 Defina o espaço amostral e identifique se os eventos são independentes.',
                'física': '⚡ Identifique as grandezas físicas e as leis aplicáveis.',
                'química': '🧪 Analise as reações e identifique os reagentes e produtos.'
            }
            
            tip = topic_tips.get(topic.lower(), '💡 Leia atentamente e identifique os conceitos principais.')
            st.markdown(f"💡 **Dica específica:** {tip}")
    
    @staticmethod
    def _display_analysis(exercise: ExerciseQuestion):
        """Exibe análise detalhada do exercício"""
        st.markdown("#### 📊 Análise do Exercício")
        
        # Métricas de qualidade
        quality_score = ImprovedExerciseDisplay._calculate_quality_score(exercise)
        valid_alternatives = sum(1 for alt in exercise.alternativas if alt.is_valid)
        avg_confidence = sum(alt.confidence for alt in exercise.alternativas) / len(exercise.alternativas) if exercise.alternativas else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Qualidade Geral", f"{quality_score}%")
        
        with col2:
            st.metric("Alternativas Válidas", f"{valid_alternatives}/{len(exercise.alternativas)}")
        
        with col3:
            st.metric("Confiança Média", f"{int(avg_confidence * 100)}%")
        
        # Gráfico de confiança das alternativas
        if exercise.alternativas:
            st.markdown("**Confiança por Alternativa:**")
            confidence_data = {alt.letra: alt.confidence for alt in exercise.alternativas}
            st.bar_chart(confidence_data)
    
    @staticmethod
    def _calculate_quality_score(exercise: ExerciseQuestion) -> int:
        """Calcula score de qualidade do exercício"""
        score = 0
        
        # Enunciado (30 pontos)
        if len(exercise.enunciado) >= 50:
            score += 30
        elif len(exercise.enunciado) >= 20:
            score += 15
        
        # Alternativas (40 pontos)
        if len(exercise.alternativas) >= 5:
            score += 20
        elif len(exercise.alternativas) >= 3:
            score += 15
        
        valid_alternatives = sum(1 for alt in exercise.alternativas if alt.is_valid)
        if valid_alternatives >= 4:
            score += 20
        elif valid_alternatives >= 3:
            score += 15
        elif valid_alternatives >= 2:
            score += 10
        
        # Metadados (30 pontos)
        if exercise.topicos_chave:
            score += 10
        if exercise.dificuldade_estimada:
            score += 10
        if exercise.habilidade_associada:
            score += 10
        
        return min(100, score)

def display_exercises_list(exercises: List[ExerciseQuestion], title: str = "📝 Exercícios Encontrados"):
    """
    Exibe uma lista de exercícios estruturados
    """
    if not exercises:
        st.info("Nenhum exercício encontrado para os critérios especificados.")
        return
    
    st.markdown(f"### {title}")
    st.success(f"✅ **{len(exercises)} exercícios encontrados**")
    
    # Estatísticas rápidas
    areas = {}
    difficulties = {}
    for ex in exercises:
        areas[ex.area_conhecimento] = areas.get(ex.area_conhecimento, 0) + 1
        difficulties[ex.dificuldade_estimada] = difficulties.get(ex.dificuldade_estimada, 0) + 1
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Por Área:**")
        for area, count in areas.items():
            short_area = area.replace(' E SUAS TECNOLOGIAS', '')
            st.markdown(f"• {short_area}: {count}")
    
    with col2:
        st.markdown("**Por Dificuldade:**")
        for diff, count in difficulties.items():
            emoji = "🟢" if diff == "Fácil" else "🟡" if diff == "Médio" else "🔴"
            st.markdown(f"• {emoji} {diff}: {count}")
    
    st.markdown("---")
    
    # Exibe cada exercício
    for i, exercise in enumerate(exercises):
        unique_id = f"exercise_{exercise.numero_questao}_{exercise.ano}_{i}"
        
        with st.expander(f"📝 {exercise.id_questao} - ENEM {exercise.ano} ({exercise.dificuldade_estimada})", expanded=False):
            ImprovedExerciseDisplay.display_structured_exercise(exercise, i+1, unique_id) 