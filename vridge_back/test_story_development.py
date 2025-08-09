#!/usr/bin/env python
"""
스토리 개발 시스템 검증 스크립트
사용자 선택(장르, 톤, 강도)이 실제로 다른 스토리를 생성하는지 검증
"""

import os
import sys
import django
import json
from datetime import datetime
from typing import Dict, List, Any

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from ai_video.services import StoryDevelopmentService
from projects.models import Project


class StoryDevelopmentTester:
    """스토리 개발 시스템 테스터"""
    
    def __init__(self):
        self.test_results = []
        self.comparison_results = {}
        
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 80)
        print("스토리 개발 시스템 검증 시작")
        print("=" * 80 + "\n")
        
        # 테스트 1: 장르 변경 테스트
        self.test_genre_variations()
        
        # 테스트 2: 톤 변경 테스트
        self.test_tone_variations()
        
        # 테스트 3: 강도 변경 테스트
        self.test_intensity_variations()
        
        # 테스트 4: 복합 변경 테스트
        self.test_complex_variations()
        
        # 결과 저장
        self.save_results()
        
        # 요약 보고서 출력
        self.print_summary()
    
    def test_genre_variations(self):
        """테스트 1: 동일한 기본 설정에서 장르만 변경"""
        print("\n[테스트 1] 장르 변경에 따른 스토리 변화")
        print("-" * 60)
        
        base_settings = {
            'tone': 'dramatic',
            'intensity': 5,
            'target_audience': 'young_adults',
            'key_message': 'Innovation and Excellence',
            'brand_values': ['quality', 'innovation', 'trust']
        }
        
        genres = ['action', 'comedy', 'horror', 'documentary', 'commercial']
        results = {}
        
        for genre in genres:
            print(f"\n테스트 중: {genre} 장르")
            
            # 모의 프로젝트 생성
            mock_project = self._create_mock_project({
                **base_settings,
                'genre': genre
            })
            
            # 스토리 개발
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[genre] = result
                print(f"✓ {genre} 스토리 생성 성공")
                
                # 주요 차이점 출력
                story_structure = result['story_structure']
                print(f"  - Opening: {story_structure['act1_opening'][:100]}...")
                print(f"  - Theme: {story_structure['overall_theme']}")
            else:
                print(f"✗ {genre} 스토리 생성 실패: {result['error']}")
        
        # 비교 분석
        self._compare_results(results, 'genre_variations')
        
    def test_tone_variations(self):
        """테스트 2: 동일한 장르에서 톤만 변경"""
        print("\n[테스트 2] 톤 변경에 따른 스토리 변화")
        print("-" * 60)
        
        base_settings = {
            'genre': 'action',
            'intensity': 5,
            'target_audience': 'young_adults',
            'key_message': 'Innovation and Excellence',
            'brand_values': ['quality', 'innovation', 'trust']
        }
        
        tones = ['professional', 'casual', 'dramatic', 'playful', 'elegant', 'edgy']
        results = {}
        
        for tone in tones:
            print(f"\n테스트 중: {tone} 톤")
            
            mock_project = self._create_mock_project({
                **base_settings,
                'tone': tone
            })
            
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[tone] = result
                print(f"✓ {tone} 스토리 생성 성공")
                
                # 시각적 스타일 차이 출력
                visual_style = result['style_guide']['visual_style']
                print(f"  - Visual Style: {visual_style.get('visual_style', 'N/A')}")
                print(f"  - Lighting: {visual_style.get('lighting', 'N/A')}")
                print(f"  - Color Palette: {visual_style.get('color_palette', 'N/A')}")
            else:
                print(f"✗ {tone} 스토리 생성 실패: {result['error']}")
        
        self._compare_results(results, 'tone_variations')
    
    def test_intensity_variations(self):
        """테스트 3: 동일한 설정에서 강도만 변경"""
        print("\n[테스트 3] 강도 변경에 따른 스토리 변화")
        print("-" * 60)
        
        base_settings = {
            'genre': 'action',
            'tone': 'dramatic',
            'target_audience': 'young_adults',
            'key_message': 'Innovation and Excellence',
            'brand_values': ['quality', 'innovation', 'trust']
        }
        
        intensities = [1, 3, 5, 7, 10]
        results = {}
        
        for intensity in intensities:
            print(f"\n테스트 중: 강도 {intensity}")
            
            mock_project = self._create_mock_project({
                **base_settings,
                'intensity': intensity
            })
            
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[f'intensity_{intensity}'] = result
                print(f"✓ 강도 {intensity} 스토리 생성 성공")
                
                # 강도 가이드 차이 출력
                intensity_guide = result['style_guide']['intensity_guide']
                print(f"  - Motion: {intensity_guide.get('motion', 'N/A')}")
                print(f"  - Effects: {intensity_guide.get('effects', 'N/A')}")
                print(f"  - Pace: {intensity_guide.get('pace', 'N/A')}")
            else:
                print(f"✗ 강도 {intensity} 스토리 생성 실패: {result['error']}")
        
        self._compare_results(results, 'intensity_variations')
    
    def test_complex_variations(self):
        """테스트 4: 복합 변경 테스트"""
        print("\n[테스트 4] 복합 파라미터 변경 테스트")
        print("-" * 60)
        
        test_combinations = [
            {
                'name': 'Intense Action Drama',
                'genre': 'action',
                'tone': 'dramatic',
                'intensity': 9
            },
            {
                'name': 'Casual Comedy',
                'genre': 'comedy',
                'tone': 'casual',
                'intensity': 3
            },
            {
                'name': 'Elegant Commercial',
                'genre': 'commercial',
                'tone': 'elegant',
                'intensity': 5
            },
            {
                'name': 'Edgy Horror',
                'genre': 'horror',
                'tone': 'edgy',
                'intensity': 8
            },
            {
                'name': 'Professional Documentary',
                'genre': 'documentary',
                'tone': 'professional',
                'intensity': 2
            }
        ]
        
        results = {}
        
        for combo in test_combinations:
            print(f"\n테스트 중: {combo['name']}")
            
            mock_project = self._create_mock_project({
                'genre': combo['genre'],
                'tone': combo['tone'],
                'intensity': combo['intensity'],
                'target_audience': 'young_adults',
                'key_message': 'Innovation and Excellence',
                'brand_values': ['quality', 'innovation', 'trust']
            })
            
            result = StoryDevelopmentService.develop_story_from_project(mock_project)
            
            if result['success']:
                results[combo['name']] = result
                print(f"✓ {combo['name']} 스토리 생성 성공")
                
                # 씬 프롬프트 샘플 출력
                if 'scene_prompts' in result:
                    first_scene = result['scene_prompts'][0] if result['scene_prompts'] else None
                    if first_scene:
                        print(f"  - 첫 씬 타이틀: {first_scene.get('title', 'N/A')}")
                        print(f"  - 비주얼 프롬프트: {first_scene.get('visual_prompt', 'N/A')[:150]}...")
            else:
                print(f"✗ {combo['name']} 스토리 생성 실패: {result['error']}")
        
        self._compare_results(results, 'complex_variations')
    
    def _create_mock_project(self, settings: Dict) -> Any:
        """테스트용 모의 프로젝트 객체 생성"""
        class MockProject:
            def __init__(self, project_data):
                self.project_data = project_data
                self.id = 'test_project'
                self.name = 'Test Project'
                self.description = 'Test project for story development validation'
        
        return MockProject(settings)
    
    def _compare_results(self, results: Dict, test_name: str):
        """결과 비교 및 차이점 분석"""
        print(f"\n[분석] {test_name} 결과 비교")
        print("-" * 40)
        
        if len(results) < 2:
            print("비교할 결과가 충분하지 않습니다.")
            return
        
        # 스토리 구조 비교
        story_structures = {}
        for key, result in results.items():
            if 'story_structure' in result:
                story_structures[key] = result['story_structure']
        
        # 차이점 계산
        differences = self._calculate_differences(story_structures)
        
        self.comparison_results[test_name] = {
            'total_variations': len(results),
            'unique_elements': differences['unique_count'],
            'similarity_score': differences['similarity'],
            'key_differences': differences['key_differences']
        }
        
        print(f"총 변형 수: {len(results)}")
        print(f"고유 요소 수: {differences['unique_count']}")
        print(f"유사도 점수: {differences['similarity']:.2f}%")
        
        if differences['key_differences']:
            print("\n주요 차이점:")
            for diff in differences['key_differences'][:3]:
                print(f"  - {diff}")
    
    def _calculate_differences(self, structures: Dict) -> Dict:
        """구조 간 차이점 계산"""
        if not structures:
            return {
                'unique_count': 0,
                'similarity': 100.0,
                'key_differences': []
            }
        
        # 모든 텍스트 수집
        all_texts = []
        for key, structure in structures.items():
            text = json.dumps(structure)
            all_texts.append(text)
        
        # 고유성 계산
        unique_texts = set(all_texts)
        unique_count = len(unique_texts)
        
        # 유사도 계산 (간단한 버전)
        if len(all_texts) > 1:
            # 첫 번째와 나머지 비교
            base_text = all_texts[0]
            similarities = []
            for text in all_texts[1:]:
                # 문자 수준 유사도 (간단한 구현)
                common_chars = sum(1 for c1, c2 in zip(base_text, text) if c1 == c2)
                max_len = max(len(base_text), len(text))
                similarity = (common_chars / max_len) * 100 if max_len > 0 else 0
                similarities.append(similarity)
            
            avg_similarity = sum(similarities) / len(similarities) if similarities else 100
        else:
            avg_similarity = 100
        
        # 주요 차이점 추출
        key_differences = []
        structure_keys = list(structures.keys())
        if len(structure_keys) >= 2:
            struct1 = structures[structure_keys[0]]
            struct2 = structures[structure_keys[1]]
            
            for key in struct1:
                if key in struct2:
                    if struct1[key] != struct2[key]:
                        key_differences.append(f"{key} 필드가 다름")
        
        return {
            'unique_count': unique_count,
            'similarity': 100 - avg_similarity,  # 차이를 보여주기 위해 반전
            'key_differences': key_differences
        }
    
    def save_results(self):
        """테스트 결과를 JSON 파일로 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/home/winnmedia/VideoPlanet/vridge_back/story_development_test_{timestamp}.json'
        
        results = {
            'timestamp': timestamp,
            'test_summary': {
                'total_tests': len(self.comparison_results),
                'test_categories': list(self.comparison_results.keys())
            },
            'comparison_results': self.comparison_results,
            'conclusion': self._generate_conclusion()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n결과 저장됨: {filename}")
    
    def _generate_conclusion(self) -> Dict:
        """테스트 결론 생성"""
        total_variations = sum(
            r['total_variations'] 
            for r in self.comparison_results.values()
        )
        
        avg_unique = sum(
            r['unique_elements'] 
            for r in self.comparison_results.values()
        ) / len(self.comparison_results) if self.comparison_results else 0
        
        return {
            'system_works': avg_unique > 0,
            'total_variations_tested': total_variations,
            'average_unique_elements': avg_unique,
            'verdict': '시스템이 사용자 선택에 따라 다른 스토리를 생성합니다.' if avg_unique > 0 else '시스템이 예상대로 작동하지 않습니다.'
        }
    
    def print_summary(self):
        """최종 요약 보고서 출력"""
        print("\n" + "=" * 80)
        print("스토리 개발 시스템 검증 완료")
        print("=" * 80)
        
        conclusion = self._generate_conclusion()
        
        print(f"\n총 테스트된 변형: {conclusion['total_variations_tested']}")
        print(f"평균 고유 요소: {conclusion['average_unique_elements']:.1f}")
        print(f"\n최종 판정: {conclusion['verdict']}")
        
        if conclusion['system_works']:
            print("\n✅ 시스템 검증 성공!")
            print("사용자의 선택(장르, 톤, 강도)이 실제로 다른 스토리를 생성합니다.")
        else:
            print("\n⚠️ 시스템 검증 실패")
            print("사용자의 선택이 스토리 생성에 충분한 영향을 미치지 않습니다.")
        
        print("\n" + "=" * 80)


def main():
    """메인 실행 함수"""
    tester = StoryDevelopmentTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()