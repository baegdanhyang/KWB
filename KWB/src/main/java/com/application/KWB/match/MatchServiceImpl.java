package com.application.KWB.match;


import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;


@Service
public class MatchServiceImpl implements MatchService{
	
	@Autowired
	private MatchDAO matchDAO;

	@Override
	public List<GameDateDto> getMatchesByMonth(int month) {
	    List<GameDto> games = matchDAO.getGamesByMonth(month);  

	    Map<String, List<GameDto>> groupedByDate = new LinkedHashMap<>();

	    for (GameDto game : games) {
	        String date = game.getDate();  // matchDate가 String이라고 가정
	        // 해당 날짜 키가 없으면 새 리스트 생성 후 추가
	        if (!groupedByDate.containsKey(date)) {
	            groupedByDate.put(date, new ArrayList<>());
	        }
	        // 해당 날짜 리스트에 게임 추가
	        groupedByDate.get(date).add(game);
	    }
	    
	    List<GameDateDto> gameDates = new ArrayList<>();
	    for (Map.Entry<String, List<GameDto>> entry : groupedByDate.entrySet()) {
	        GameDateDto gameDateDto = new GameDateDto();
	        gameDateDto.setDate(entry.getKey());
	        gameDateDto.setGames(entry.getValue());
	        gameDates.add(gameDateDto);
	    }

	    return gameDates;
	}

	

}
