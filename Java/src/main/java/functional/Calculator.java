package functional;

import functional.classes.*;
import maker.CSVMaker;
import maker.CSVPartlyMaker;
import maker.NewJSONMaker;
import maker.NewJSONPartlyMaker;
import maker.SQLMaker;
import maker.SQLPartlyMaker;
import visual.classes.LoadType;

import org.jgrapht.GraphPath;
import org.jgrapht.alg.interfaces.ShortestPathAlgorithm.SingleSourcePaths;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultEdge;
import org.jgrapht.graph.SimpleDirectedWeightedGraph;

import com.google.gson.JsonObject;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

public class Calculator {
	
	static Integer finalCount = 1;
	
	public static void calculateAndOutputToFiles(ArrayList<Location> locations, 
												ArrayList<TravelData> dataAll,
												LoadType loadTypes,
												String csvFolderPath,
				                                String jsonFolderPath, 
				                                String sqlFolderPath,
				                                String routeType) {
		DijkstraShortestPath<Integer, CheapTripWeightedEdge> dsp = Calculator.buildGraph(locations, dataAll);
    	
		CSVPartlyMaker.settingFile(csvFolderPath, routeType);
    	NewJSONPartlyMaker.settingFile(jsonFolderPath,routeType);
    	SQLPartlyMaker.settingFile(sqlFolderPath,routeType);
    	for (Location location : locations) {
    		ArrayList<Route> routes = Calculator.calculateRoutesForOneVertex(location, dsp);
            if (loadTypes.isCsvLoad() && !csvFolderPath.equals("")) {
                CSVMaker.routesToFile(CSVMaker.routesToCSV(routes), csvFolderPath, routeType);
            }
            if (loadTypes.isJsonLoad() && !jsonFolderPath.equals("")) {
            	if (location.equals(locations.get(locations.size()-1))){
            		NewJSONPartlyMaker.jsonToFile(routes,jsonFolderPath,routeType,false);
            	} else {
            		NewJSONPartlyMaker.jsonToFile(routes,jsonFolderPath,routeType,true);
            	}
                try {
                    NewJSONMaker.routesJsonPartly(routes,locations,jsonFolderPath,routeType);
                } catch (IOException ex) {
                    throw new RuntimeException(ex);
                }
            }
            if (loadTypes.isSqlLoad() && !jsonFolderPath.equals("")) {
                SQLPartlyMaker.routesSQL(routes,sqlFolderPath,routeType);
            }
		}
    	
    	CSVPartlyMaker.endingFile( csvFolderPath, routeType);
    	NewJSONPartlyMaker.endingFile(jsonFolderPath,routeType);
    	SQLPartlyMaker.endingFile(sqlFolderPath,routeType);
    	finalCount = 1;
	}
	
	public static ArrayList<Route> calculateRoutesForOneVertex(Location vertexFrom,
			DijkstraShortestPath<Integer, CheapTripWeightedEdge> dsp){
		
		ArrayList<Route> routes_final = new ArrayList<>();
		SingleSourcePaths<Integer, CheapTripWeightedEdge> sourcePathGraph = dsp.getPaths(vertexFrom.getId());
		Set<Integer> vertexSet =  sourcePathGraph.getGraph().vertexSet();
		for (Integer vertexTo : vertexSet) {
			if (vertexFrom.getId() == vertexTo || sourcePathGraph.getPath(vertexTo) == null) {
				continue;
			}
			List<CheapTripWeightedEdge> fromToEdgesList = sourcePathGraph.getPath(vertexTo).getEdgeList();
			if(fromToEdgesList.isEmpty()) {
				continue;
			}
			AtomicInteger fromToduration = new AtomicInteger(0);
			StringBuilder travelData = new StringBuilder();
			fromToEdgesList.forEach(e -> {
				fromToduration.addAndGet(e.getDuration());
				travelData.append(e.getMyId());
				travelData.append(",");
			});
			travelData.deleteCharAt(travelData.length() - 1);
			float totalPrice = (float) sourcePathGraph.getPath(vertexTo).getWeight();

			Route route = new Route(finalCount, vertexFrom.getId(), vertexTo, totalPrice,
					fromToduration.get(), travelData.toString());
			routes_final.add(route);
			finalCount++;
		}
		return routes_final;
	}
	
	public static DijkstraShortestPath<Integer, CheapTripWeightedEdge> buildGraph(ArrayList<Location> locations,
			ArrayList<TravelData> directRoutes) {
		SimpleDirectedWeightedGraph<Integer, CheapTripWeightedEdge> graph = new SimpleDirectedWeightedGraph<>(
				CheapTripWeightedEdge.class);
		locations.forEach(l -> {
			graph.addVertex(l.getId());
		});

		directRoutes.forEach(route -> {
			if (graph.containsEdge(route.getFrom(), route.getTo())) {
				CheapTripWeightedEdge e = graph.getEdge(route.getFrom(), route.getTo());
				if (graph.getEdgeWeight(e) > route.getEuro_price()) {
					graph.setEdgeWeight(e, route.getEuro_price());
					e.setMyId(route.getId());
					e.setDuration(route.getTime_in_minutes());
				}
			} else {
				graph.addEdge(route.getFrom(), route.getTo()).setMyId(route.getId());
				graph.getEdge(route.getFrom(), route.getTo()).setDuration(route.getTime_in_minutes());
				graph.setEdgeWeight(route.getFrom(), route.getTo(), route.getEuro_price());
			}
		});

		DijkstraShortestPath<Integer, CheapTripWeightedEdge> dsp = new DijkstraShortestPath<Integer, CheapTripWeightedEdge>(
				graph);
		return dsp;
	}

	public static ArrayList<Route> calculateRoutes(ArrayList<Location> locations, ArrayList<TravelData> directRoutes) {
		DijkstraShortestPath<Integer, CheapTripWeightedEdge> dsp = buildGraph(locations, directRoutes);
		ArrayList<Route> routes_final = new ArrayList<>();
		int finalCount = 1;

		for (Location vertexFrom : locations) {
			SingleSourcePaths<Integer, CheapTripWeightedEdge> sourcePathGraph = dsp.getPaths(vertexFrom.getId());
			Set<Integer> vertexSet =  sourcePathGraph.getGraph().vertexSet();
			for (Integer vertexTo : vertexSet) {
				if (vertexFrom.getId() == vertexTo) {
					continue;
				}
				List<CheapTripWeightedEdge> fromToEdgesList = sourcePathGraph.getPath(vertexTo).getEdgeList();
				if(fromToEdgesList.isEmpty()) {
					continue;
				}
				AtomicInteger fromToduration = new AtomicInteger(0);
				StringBuilder travelData = new StringBuilder();
				fromToEdgesList.forEach(e -> {
					fromToduration.addAndGet(e.getDuration());
					travelData.append(e.getMyId());
					travelData.append(",");
				});
				travelData.deleteCharAt(travelData.length() - 1);
				float totalPrice = (float) sourcePathGraph.getPath(vertexTo).getWeight();

				Route route = new Route(finalCount, vertexFrom.getId(), vertexTo, totalPrice,
						fromToduration.get(), travelData.toString());
				routes_final.add(route);
				finalCount++;
			}
		}
		return routes_final;
	}

	public static ArrayList<TravelData> getFlyingData(ArrayList<TravelData> input) {
		ArrayList<TravelData> result = new ArrayList<>();
		for (int i = 0; i < input.size(); i++) {
			TravelData data = input.get(i);
			if (data.getTransportation_type() == 1) {
				result.add(data);
			}
		}
		return result;
	}

	public static ArrayList<TravelData> getFixedDataWithoutRideShare(ArrayList<TravelData> input) {
		ArrayList<TravelData> result = new ArrayList<>();
		for (int i = 0; i < input.size(); i++) {
			TravelData data = input.get(i);
			if ((data.getTransportation_type() != 1) && (data.getTransportation_type() != 8)) {
				result.add(data);
			}
		}
		return result;
	}

	public static ArrayList<TravelData> getDataWithoutRideShare(ArrayList<TravelData> input) {
		ArrayList<TravelData> result = new ArrayList<>();
		for (int i = 0; i < input.size(); i++) {
			TravelData data = input.get(i);
			if (data.getTransportation_type() != 8) {
				result.add(data);
			}
		}
		return result;
	}

	public static void counting(HashMap<Integer, Integer> counter, int travelData) {
		if (!counter.containsKey(travelData)) {
			counter.put(travelData, 1);
		} else {
			int count = counter.get(travelData);
			counter.put(travelData, count + 1);
		}
	}
}
