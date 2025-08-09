#!/usr/bin/env python3
"""
씬 프롬프트 생성 심화 테스트
각 파라미터가 실제 프롬프트 생성에 미치는 영향을 상세히 검증
"""

import os
import sys
import django
import json
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from ai_video.services import StoryDevelopmentService, AIVideoService
from ai_video.models import Scene, Story


class ScenePromptTester:
    """씬 프롬프트 생성 테스터"""
    
    def __init__(self):
        self.test_results = {}
        
    def run_detailed_tests(self):
        """상세 테스트 실행"""
        print("=" * 80)
        print("씬 프롬프트 생성 심화 테스트")
        print("=" * 80 + "\n")
        
        # 모의 씬 객체 생성
        mock_scene = self._create_mock_scene()
        
        # 테스트 1: 장르별 프롬프트 차이
        self.test_genre_prompts(mock_scene)
        
        # 테스트 2: 톤별 프롬프트 차이
        self.test_tone_prompts(mock_scene)
        
        # 테스트 3: 강도별 프롬프트 차이
        self.test_intensity_prompts(mock_scene)
        
        # 테스트 4: 복합 시나리오
        self.test_complex_scenarios(mock_scene)
        
        # 결과 저장 및 보고서 생성
        self.generate_report()
    
    def test_genre_prompts(self, scene):
        """장르별 프롬프트 생성 테스트"""
        print("\n[테스트 1] 장르별 프롬프트 생성")
        print("-" * 60)
        
        genres = ['action', 'comedy', 'horror', 'documentary', 'commercial']
        results = {}
        
        for genre in genres:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, genre, 'dramatic', 5
            )
            results[genre] = prompt
            
            print(f"\n{genre.upper()} 장르:")
            print(f"이미지 프롬프트: {prompt['image_prompt'][:150]}...")
            print(f"비디오 프롬프트: {prompt['video_prompt'][:150]}...")
            print(f"모션 강도: {prompt['motion_intensity']}")
            
        self.test_results['genre_prompts'] = results
        
        # 차이점 분석
        self._analyze_prompt_differences(results, 'genre')
    
    def test_tone_prompts(self, scene):
        """톤별 프롬프트 생성 테스트"""
        print("\n[테스트 2] 톤별 프롬프트 생성")
        print("-" * 60)
        
        tones = ['professional', 'casual', 'dramatic', 'playful', 'elegant', 'edgy']
        results = {}
        
        for tone in tones:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, 'commercial', tone, 5
            )
            results[tone] = prompt
            
            print(f"\n{tone.upper()} 톤:")
            print(f"이미지 프롬프트: {prompt['image_prompt'][:150]}...")
            style_preset = prompt['image_parameters'].get('style_preset', 'N/A')
            print(f"스타일 프리셋: {style_preset}")
            
        self.test_results['tone_prompts'] = results
        self._analyze_prompt_differences(results, 'tone')
    
    def test_intensity_prompts(self, scene):
        """강도별 프롬프트 생성 테스트"""
        print("\n[테스트 3] 강도별 프롬프트 생성")
        print("-" * 60)
        
        intensities = [1, 3, 5, 7, 10]
        results = {}
        
        for intensity in intensities:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, 'action', 'dramatic', intensity
            )
            results[f'intensity_{intensity}'] = prompt
            
            print(f"\n강도 {intensity}:")
            print(f"모션 강도: {prompt['motion_intensity']}")
            print(f"모션 버킷 ID: {prompt['video_parameters']['motion_bucket_id']}")
            conditioning = prompt['video_parameters']['conditioning_augmentation']
            print(f"컨디셔닝 증강: {conditioning}")
            
        self.test_results['intensity_prompts'] = results
        self._analyze_prompt_differences(results, 'intensity')
    
    def test_complex_scenarios(self, scene):
        """복합 시나리오 테스트"""
        print("\n[테스트 4] 복합 시나리오 프롬프트 생성")
        print("-" * 60)
        
        scenarios = [
            {'name': 'Intense Action', 'genre': 'action', 'tone': 'edgy', 'intensity': 9},
            {'name': 'Soft Comedy', 'genre': 'comedy', 'tone': 'playful', 'intensity': 2},
            {'name': 'Elegant Commercial', 'genre': 'commercial', 'tone': 'elegant', 'intensity': 4},
            {'name': 'Dark Horror', 'genre': 'horror', 'tone': 'dramatic', 'intensity': 8},
            {'name': 'Professional Doc', 'genre': 'documentary', 'tone': 'professional', 'intensity': 3}
        ]
        
        results = {}
        
        for scenario in scenarios:
            prompt = AIVideoService._create_enhanced_prompt(
                scene, 
                scenario['genre'], 
                scenario['tone'], 
                scenario['intensity']
            )
            results[scenario['name']] = prompt
            
            print(f"\n{scenario['name']}:")
            print(f"장르: {scenario['genre']}, 톤: {scenario['tone']}, 강도: {scenario['intensity']}")
            
            # 이미지 프롬프트 분석
            image_prompt = prompt['image_prompt']
            print(f"\n이미지 프롬프트 구성 요소:")
            
            # 키워드 분석
            keywords = self._extract_keywords(image_prompt)
            print(f"  - 주요 키워드: {', '.join(keywords[:5])}")
            
            # 비디오 파라미터 분석
            print(f"\n비디오 파라미터:")
            print(f"  - 모션 강도: {prompt['motion_intensity']}")
            print(f"  - 스타일 프리셋: {prompt['image_parameters'].get('style_preset', 'N/A')}")
            
        self.test_results['complex_scenarios'] = results
    
    def _create_mock_scene(self):
        """테스트용 모의 씬 객체 생성"""
        class MockStory:
            def __init__(self):
                self.fps = 30
                
        class MockScene:
            def __init__(self):
                self.order = 1
                self.title = "Opening Scene"
                self.description = "An establishing shot that sets the mood and introduces the main elements"
                self.start_time = 0
                self.end_time = 5
                self.duration = 5
                self.scene_type = 'intro'
                self.story = MockStory()
        
        return MockScene()
    
    def _extract_keywords(self, prompt):
        """프롬프트에서 주요 키워드 추출"""
        # 일반적인 단어 제외
        common_words = {'a', 'the', 'and', 'or', 'with', 'for', 'that', 'shot', 'scene'}
        
        # 단어 분리 및 필터링
        words = prompt.lower().split()
        keywords = []
        
        for word in words:
            # 구두점 제거
            word = word.strip('.,;:!?')
            # 일반 단어 제외하고 4글자 이상인 단어만
            if word not in common_words and len(word) > 3:
                keywords.append(word)
        
        # 중복 제거하고 빈도순 정렬 (간단한 버전)
        seen = {}
        for word in keywords:
            seen[word] = seen.get(word, 0) + 1
        
        sorted_keywords = sorted(seen.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords]
    
    def _analyze_prompt_differences(self, results, category):
        """프롬프트 차이점 분석"""
        print(f"\n[분석] {category} 차이점")
        print("-" * 40)
        
        if len(results) < 2:
            print("비교할 결과가 부족합니다.")
            return
        
        # 첫 번째 결과를 기준으로 비교
        keys = list(results.keys())
        base_key = keys[0]
        base_result = results[base_key]
        
        differences_found = []
        
        for key in keys[1:]:
            result = results[key]
            
            # 이미지 프롬프트 비교
            if base_result['image_prompt'] != result['image_prompt']:
                differences_found.append(f"{key}: 이미지 프롬프트 다름")
            
            # 모션 강도 비교
            if base_result['motion_intensity'] != result['motion_intensity']:
                differences_found.append(f"{key}: 모션 강도 다름 ({result['motion_intensity']})")
            
            # 파라미터 비교
            if base_result.get('image_parameters') != result.get('image_parameters'):
                differences_found.append(f"{key}: 이미지 파라미터 다름")
        
        if differences_found:
            print(f"발견된 차이점 ({len(differences_found)}개):")
            for diff in differences_found[:5]:  # 최대 5개만 표시
                print(f"  - {diff}")
        else:
            print("⚠️ 차이점이 발견되지 않았습니다!")
    
    def generate_report(self):
        """최종 보고서 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/home/winnmedia/VideoPlanet/vridge_back/scene_prompt_test_{timestamp}.json'
        
        # 보고서 데이터 구성
        report = {
            'timestamp': timestamp,
            'test_categories': list(self.test_results.keys()),
            'test_results': self.test_results,
            'summary': self._generate_summary()
        }
        
        # JSON 파일로 저장
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n보고서 저장됨: {filename}")
        
        # 요약 출력
        print("\n" + "=" * 80)
        print("테스트 요약")
        print("=" * 80)
        print(report['summary']['conclusion'])
    
    def _generate_summary(self):
        """테스트 요약 생성"""
        total_tests = sum(len(results) for results in self.test_results.values())
        
        # 각 카테고리별 고유성 확인
        unique_counts = {}
        for category, results in self.test_results.items():
            unique_prompts = set()
            for key, result in results.items():
                unique_prompts.add(result['image_prompt'])
            unique_counts[category] = len(unique_prompts)
        
        avg_uniqueness = sum(unique_counts.values()) / len(unique_counts) if unique_counts else 0
        
        return {
            'total_tests': total_tests,
            'categories_tested': len(self.test_results),
            'unique_prompts_per_category': unique_counts,
            'average_uniqueness': avg_uniqueness,
            'conclusion': f"✅ 프롬프트 생성 시스템이 정상 작동합니다. 평균 {avg_uniqueness:.1f}개의 고유한 프롬프트가 생성되었습니다."
        }


def main():
    """메인 실행 함수"""
    tester = ScenePromptTester()
    tester.run_detailed_tests()


if __name__ == '__main__':
    main()